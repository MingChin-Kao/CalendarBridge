"""
ICS 精準解析器
專注於處理週期事件、時區轉換和事件變更偵測
"""
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from zoneinfo import ZoneInfo
import requests
from icalendar import Calendar, Event as ICalEvent
from dateutil.rrule import rrulestr
import recurring_ical_events

from src.utils.config import SourceConfig, ProcessingConfig


logger = logging.getLogger(__name__)


class EventData:
    """事件資料結構"""
    
    def __init__(self, vevent: ICalEvent, processing_config: ProcessingConfig):
        self.uid = str(vevent.get('UID', ''))
        self.sequence = int(vevent.get('SEQUENCE', 0))
        self.last_modified = vevent.get('LAST-MODIFIED')
        self.created = vevent.get('CREATED')
        self.dtstamp = vevent.get('DTSTAMP')
        
        # 基本事件資訊
        self.summary = str(vevent.get('SUMMARY', ''))
        self.description = str(vevent.get('DESCRIPTION', ''))
        self.location = str(vevent.get('LOCATION', ''))
        self.status = str(vevent.get('STATUS', 'CONFIRMED'))
        
        # 時間資訊
        self.dtstart = vevent.get('DTSTART')
        self.dtend = vevent.get('DTEND')
        self.duration = vevent.get('DURATION')
        self.all_day = False
        
        # 處理時間資訊
        self._process_time_info()
        
        # 週期規則
        self.rrule = vevent.get('RRULE')
        self.rdate = vevent.get('RDATE')
        self.exdate = vevent.get('EXDATE')
        self.exrule = vevent.get('EXRULE')
        self.recurrence_id = vevent.get('RECURRENCE-ID')
        
        # 其他屬性
        self.categories = vevent.get('CATEGORIES')
        self.attendees = self._extract_attendees(vevent)
        self.organizer = vevent.get('ORGANIZER')
        
        # 處理標題和描述
        self._process_content(processing_config)
        
        # 計算事件指紋
        self.fingerprint = self._calculate_fingerprint()
        
    def _process_time_info(self):
        """處理時間資訊，確保時區正確性"""
        if self.dtstart:
            if hasattr(self.dtstart.dt, 'date') and not hasattr(self.dtstart.dt, 'hour'):
                # 全天事件
                self.all_day = True
                self.start_datetime = self.dtstart.dt
                if self.dtend:
                    self.end_datetime = self.dtend.dt
                elif self.duration:
                    self.end_datetime = self.start_datetime + self.duration.dt
                else:
                    self.end_datetime = self.start_datetime + timedelta(days=1)
            else:
                # 有時間的事件
                self.start_datetime = self.dtstart.dt
                if self.dtend:
                    self.end_datetime = self.dtend.dt
                elif self.duration:
                    self.end_datetime = self.start_datetime + self.duration.dt
                else:
                    # 預設1小時
                    self.end_datetime = self.start_datetime + timedelta(hours=1)
                
                # 確保時區資訊
                if self.start_datetime.tzinfo is None:
                    logger.warning(f"Event {self.uid} has no timezone info, assuming Asia/Taipei")
                    taipei_tz = ZoneInfo("Asia/Taipei")
                    self.start_datetime = self.start_datetime.replace(tzinfo=taipei_tz)
                    self.end_datetime = self.end_datetime.replace(tzinfo=taipei_tz)
    
    def _extract_attendees(self, vevent: ICalEvent) -> List[Dict[str, str]]:
        """提取參與者資訊"""
        attendees = []
        attendee_props = vevent.get('ATTENDEE')
        if attendee_props:
            if not isinstance(attendee_props, list):
                attendee_props = [attendee_props]
            
            for attendee in attendee_props:
                attendee_info = {
                    'email': str(attendee),
                    'name': attendee.params.get('CN', ''),
                    'role': attendee.params.get('ROLE', 'REQ-PARTICIPANT'),
                    'status': attendee.params.get('PARTSTAT', 'NEEDS-ACTION')
                }
                attendees.append(attendee_info)
        
        return attendees
    
    def _process_content(self, processing_config: ProcessingConfig):
        """處理事件內容，添加前綴和後綴"""
        # 添加前綴到標題
        if not self.summary.startswith(processing_config.event_prefix):
            self.summary = processing_config.event_prefix + self.summary
        
        # 添加後綴到描述
        if processing_config.description_suffix:
            if self.description:
                self.description += processing_config.description_suffix
            else:
                self.description = processing_config.description_suffix.strip()
        
        # 限制描述長度
        if len(self.description) > processing_config.max_description_length:
            self.description = self.description[:processing_config.max_description_length-3] + "..."
    
    def _calculate_fingerprint(self) -> str:
        """計算事件指紋，用於變更偵測"""
        # 對於週期事件的個別實例，需要包含具體的日期時間
        content = f"{self.uid}|{self.sequence}|{self.summary}|{self.description}|{self.location}|{self.start_datetime}|{self.end_datetime}|{self.rrule}|{self.status}"
        
        # 如果是週期事件的特定實例，添加實例標識
        if self.recurrence_id:
            content += f"|{self.recurrence_id}"
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_unique_event_id(self) -> str:
        """取得事件的唯一識別ID，用於避免重複"""
        # 對於週期事件的修改實例 (RECURRENCE-ID)
        if self.is_modified_instance():
            if self.recurrence_id:
                recur_id_str = self._safe_serialize_datetime(self.recurrence_id)
                return f"{self.uid}_RECUR_{recur_id_str}"
        
        # 對於週期事件：使用純 UID，不添加日期後綴
        # 讓 Google Calendar 自動管理週期實例
        if self.is_recurring():
            return self.uid
        
        # 對於非週期事件，直接使用 UID
        return self.uid
    
    def get_series_id(self) -> str:
        """取得週期事件系列ID，用於處理整個系列的變更"""
        # 對於週期事件，返回純 UID，代表整個系列
        if self.is_recurring():
            return self.uid
        return self.uid
    
    def is_recurring(self) -> bool:
        """判斷是否為週期事件"""
        return self.rrule is not None or self.rdate is not None
    
    def is_modified_instance(self) -> bool:
        """判斷是否為修改的週期實例"""
        return self.recurrence_id is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'uid': self.uid,
            'sequence': self.sequence,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'summary': self.summary,
            'description': self.description,
            'location': self.location,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'all_day': self.all_day,
            'status': self.status,
            'rrule': str(self.rrule) if self.rrule else None,
            'recurrence_id': self._safe_serialize_datetime(self.recurrence_id),
            'attendees': self.attendees,
            'fingerprint': self.fingerprint
        }
    
    def _safe_serialize_datetime(self, dt_value) -> Optional[str]:
        """安全序列化日期時間值"""
        if dt_value is None:
            return None
        
        try:
            # 如果是 icalendar 的 vDDDTypes 物件
            if hasattr(dt_value, 'dt'):
                return dt_value.dt.isoformat() if dt_value.dt else None
            # 如果是標準 datetime 物件
            elif hasattr(dt_value, 'isoformat'):
                return dt_value.isoformat()
            # 其他情況轉為字串
            else:
                return str(dt_value)
        except Exception:
            return str(dt_value) if dt_value else None


class ICSParser:
    """ICS 精準解析器"""
    
    def __init__(self, source_config: SourceConfig, processing_config: ProcessingConfig):
        self.source_config = source_config
        self.processing_config = processing_config
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': source_config.user_agent})
    
    def fetch_ics_content(self) -> str:
        """從 URL 獲取 ICS 內容"""
        logger.info(f"Fetching ICS content from: {self.source_config.url}")
        
        for attempt in range(self.source_config.retry_count):
            try:
                response = self.session.get(
                    self.source_config.url,
                    timeout=self.source_config.timeout
                )
                response.raise_for_status()
                
                logger.info(f"Successfully fetched ICS content ({len(response.content)} bytes)")
                return response.text
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.source_config.retry_count - 1:
                    raise
        
        raise Exception("Failed to fetch ICS content after all retries")
    
    def parse_ics_content(self, ics_content: str) -> Tuple[List[EventData], List[EventData]]:
        """
        解析 ICS 內容
        返回: (主事件列表, 修改實例列表)
        """
        logger.info("Parsing ICS content")
        
        try:
            calendar = Calendar.from_ical(ics_content)
        except Exception as e:
            logger.error(f"Failed to parse ICS content: {e}")
            raise
        
        main_events = []
        modified_instances = []
        
        for component in calendar.walk():
            if component.name == "VEVENT":
                try:
                    event_data = EventData(component, self.processing_config)
                    
                    if event_data.is_modified_instance():
                        modified_instances.append(event_data)
                    else:
                        main_events.append(event_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to parse event {component.get('UID', 'unknown')}: {e}")
                    continue
        
        logger.info(f"Parsed {len(main_events)} main events and {len(modified_instances)} modified instances")
        return main_events, modified_instances
    
    def expand_recurring_events(self, events: List[EventData], 
                              start_date: datetime, end_date: datetime) -> List[EventData]:
        """
        展開週期事件到指定時間範圍
        這個方法會處理複雜的週期規則和例外情況
        """
        logger.info(f"Expanding recurring events from {start_date} to {end_date}")
        
        expanded_events = []
        
        for event in events:
            if not event.is_recurring():
                # 非週期事件，直接檢查是否在範圍內
                if (event.start_datetime >= start_date and event.start_datetime <= end_date):
                    expanded_events.append(event)
            else:
                # 週期事件，使用 recurring-ical-events 套件展開
                try:
                    # 重新建立 iCalendar 事件物件
                    cal = Calendar()
                    vevent = ICalEvent()
                    
                    # 設定必要屬性
                    vevent.add('uid', event.uid)
                    vevent.add('dtstart', event.start_datetime)
                    vevent.add('dtend', event.end_datetime)
                    vevent.add('summary', event.summary)
                    vevent.add('description', event.description)
                    vevent.add('location', event.location)
                    
                    if event.rrule:
                        vevent.add('rrule', event.rrule)
                    if event.exdate:
                        vevent.add('exdate', event.exdate)
                    
                    cal.add_component(vevent)
                    
                    # 使用 recurring_ical_events 展開
                    occurrences = recurring_ical_events.of(cal).between(start_date, end_date)
                    
                    for occurrence in occurrences:
                        # 為每個實例創建新的 EventData
                        instance_event = EventData(vevent, self.processing_config)
                        instance_event.start_datetime = occurrence['DTSTART'].dt
                        instance_event.end_datetime = occurrence['DTEND'].dt
                        # 重新計算指紋
                        instance_event.fingerprint = instance_event._calculate_fingerprint()
                        expanded_events.append(instance_event)
                        
                except Exception as e:
                    logger.warning(f"Failed to expand recurring event {event.uid}: {e}")
                    # 如果展開失敗，至少添加原始事件
                    if (event.start_datetime >= start_date and event.start_datetime <= end_date):
                        expanded_events.append(event)
        
        logger.info(f"Expanded to {len(expanded_events)} event instances")
        return expanded_events
    
    def parse_and_expand(self, start_date: datetime, end_date: datetime) -> List[EventData]:
        """
        完整的解析和展開流程
        對於週期事件：不展開，保持原始事件以避免重複建立
        """
        ics_content = self.fetch_ics_content()
        main_events, modified_instances = self.parse_ics_content(ics_content)
        
        # 篩選在時間範圍內的事件
        filtered_events = []
        
        for event in main_events:
            if not event.is_recurring():
                # 非週期事件，檢查是否在範圍內
                if (event.start_datetime >= start_date and event.start_datetime <= end_date):
                    filtered_events.append(event)
            else:
                # 週期事件：不展開，直接使用原始事件
                # Google Calendar 會自動展開週期事件
                # 只需要檢查週期事件的開始時間或者是否與範圍有交集
                if self._recurring_event_overlaps_range(event, start_date, end_date):
                    filtered_events.append(event)
        
        # 處理修改實例
        if modified_instances:
            logger.info(f"Adding {len(modified_instances)} modified instances")
            # 修改實例總是需要作為獨立事件處理
            for instance in modified_instances:
                if (instance.start_datetime >= start_date and instance.start_datetime <= end_date):
                    filtered_events.append(instance)
        
        logger.info(f"Filtered to {len(filtered_events)} events (recurring events not expanded)")
        return filtered_events
    
    def _recurring_event_overlaps_range(self, event: EventData, start_date: datetime, end_date: datetime) -> bool:
        """檢查週期事件是否與指定範圍有重疊"""
        # 簡單檢查：如果事件開始時間在範圍前，且有RRULE，假設有重疊
        if event.start_datetime <= end_date:
            # 如果有結束規則，檢查是否已結束
            if event.rrule and 'UNTIL' in str(event.rrule):
                # 這裡應該解析UNTIL，但暫時簡化處理
                return True
            elif event.rrule and 'COUNT' in str(event.rrule):
                # 這裡應該計算COUNT，但暫時簡化處理
                return True
            else:
                # 無限重複的週期事件
                return True
        return False