"""
Google Calendar API 客戶端
處理與 Google Calendar 的所有互動
"""
import logging
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils.config import GoogleCalendarConfig
from src.parsers.ics_parser import EventData


logger = logging.getLogger(__name__)

# Google Calendar API 權限範圍
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarClient:
    """Google Calendar API 客戶端"""
    
    def __init__(self, config: GoogleCalendarConfig):
        self.config = config
        self.service = None
        self.credentials = None
        
    def authenticate(self) -> None:
        """執行 Google 認證（OAuth 或服務帳號）"""
        if self.config.auth_type == "service_account":
            self._authenticate_service_account()
        else:
            self._authenticate_oauth()
    
    def _authenticate_service_account(self) -> None:
        """服務帳號認證"""
        service_account_file = Path(self.config.service_account_file)
        
        if not service_account_file.exists():
            raise FileNotFoundError(
                f"Service account file not found: {service_account_file}\n"
                "Please download service account key from Google Cloud Console"
            )
        
        try:
            creds = service_account.Credentials.from_service_account_file(
                str(service_account_file), scopes=SCOPES
            )
            
            self.credentials = creds
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar service account authentication successful")
            
        except Exception as e:
            logger.error(f"Service account authentication failed: {e}")
            raise
    
    def _authenticate_oauth(self) -> None:
        """OAuth 認證"""
        creds = None
        token_file = Path(self.config.token_file)
        
        # 載入現有的權杖
        if token_file.exists():
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # 如果沒有有效的認證資料，執行 OAuth 流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    logger.info("Refresh token may be expired, need to re-authenticate")
                    raise
            else:
                logger.info("Starting OAuth flow")
                credentials_file = Path(self.config.credentials_file)
                
                if not credentials_file.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {credentials_file}\n"
                        "Please download credentials from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # 儲存認證資料
            token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Google Calendar OAuth authentication successful")
    
    def get_calendar_info(self, calendar_id: str = None) -> Dict[str, Any]:
        """取得行事曆資訊"""
        if not self.service:
            self.authenticate()
        
        calendar_id = calendar_id or self.config.calendar_id
        
        try:
            calendar = self.service.calendars().get(calendarId=calendar_id).execute()
            logger.info(f"Calendar info: {calendar.get('summary', 'Unknown')}")
            return calendar
        except HttpError as e:
            logger.error(f"Failed to get calendar info: {e}")
            raise
    
    def list_events(self, start_time: datetime, end_time: datetime, 
                   calendar_id: str = None) -> List[Dict[str, Any]]:
        """列出指定時間範圍內的事件"""
        if not self.service:
            self.authenticate()
        
        calendar_id = calendar_id or self.config.calendar_id
        
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                maxResults=2500  # Google API 限制
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Found {len(events)} events in Google Calendar")
            return events
            
        except HttpError as e:
            logger.error(f"Failed to list events: {e}")
            raise
    
    def create_event(self, event_data: EventData, calendar_id: str = None) -> Dict[str, Any]:
        """建立新事件"""
        if not self.service:
            self.authenticate()
        
        calendar_id = calendar_id or self.config.calendar_id
        
        # 建立 Google Calendar 事件格式
        google_event = self._convert_to_google_event(event_data)
        
        try:
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=google_event
            ).execute()
            
            logger.info(f"Created event: {created_event.get('id')} - {event_data.summary}")
            return created_event
            
        except HttpError as e:
            logger.error(f"Failed to create event {event_data.uid}: {e}")
            raise
    
    def update_event(self, google_event_id: str, event_data: EventData, 
                    calendar_id: str = None) -> Dict[str, Any]:
        """更新現有事件"""
        if not self.service:
            self.authenticate()
        
        calendar_id = calendar_id or self.config.calendar_id
        
        # 建立 Google Calendar 事件格式
        google_event = self._convert_to_google_event(event_data)
        
        try:
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=google_event_id,
                body=google_event
            ).execute()
            
            logger.info(f"Updated event: {google_event_id} - {event_data.summary}")
            return updated_event
            
        except HttpError as e:
            logger.error(f"Failed to update event {google_event_id}: {e}")
            raise
    
    def delete_event(self, google_event_id: str, calendar_id: str = None) -> None:
        """刪除事件"""
        if not self.service:
            self.authenticate()
        
        calendar_id = calendar_id or self.config.calendar_id
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=google_event_id
            ).execute()
            
            logger.info(f"Deleted event: {google_event_id}")
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Event {google_event_id} not found (already deleted?)")
            else:
                logger.error(f"Failed to delete event {google_event_id}: {e}")
                raise
    
    def batch_create_events(self, events: List[EventData], 
                          calendar_id: str = None) -> List[Dict[str, Any]]:
        """批次建立事件"""
        if not self.service:
            self.authenticate()
        
        calendar_id = calendar_id or self.config.calendar_id
        created_events = []
        
        # Google API 建議批次操作，但這裡簡化為順序操作
        for event_data in events:
            try:
                created_event = self.create_event(event_data, calendar_id)
                created_events.append(created_event)
            except Exception as e:
                logger.error(f"Failed to create event in batch: {event_data.uid} - {e}")
                continue
        
        logger.info(f"Batch created {len(created_events)} out of {len(events)} events")
        return created_events
    
    def _convert_to_google_event(self, event_data: EventData) -> Dict[str, Any]:
        """將 EventData 轉換為 Google Calendar 事件格式"""
        google_event = {
            'summary': event_data.summary,
            'description': event_data.description,
            'location': event_data.location,
            'status': self._convert_status(event_data.status),
        }
        
        # 處理時間
        if event_data.all_day:
            google_event['start'] = {
                'date': event_data.start_datetime.strftime('%Y-%m-%d')
            }
            google_event['end'] = {
                'date': event_data.end_datetime.strftime('%Y-%m-%d')
            }
        else:
            google_event['start'] = {
                'dateTime': event_data.start_datetime.isoformat(),
                'timeZone': str(event_data.start_datetime.tzinfo)
            }
            google_event['end'] = {
                'dateTime': event_data.end_datetime.isoformat(),
                'timeZone': str(event_data.end_datetime.tzinfo)
            }
        
        # 處理週期規則
        if event_data.rrule:
            try:
                # 轉換 RRULE 為 Google Calendar 格式
                rrule_str = str(event_data.rrule)
                
                # 檢查並修正 RRULE 格式
                rrule_str = self._fix_rrule_for_google(rrule_str)
                
                if rrule_str:  # 只有有效的 RRULE 才添加
                    google_event['recurrence'] = [f'RRULE:{rrule_str}']
                    
                    # 處理例外日期
                    if event_data.exdate:
                        exdate_list = event_data.exdate if isinstance(event_data.exdate, list) else [event_data.exdate]
                        for exdate in exdate_list:
                            try:
                                exdate_str = exdate.to_ical().decode() if hasattr(exdate, 'to_ical') else str(exdate)
                                google_event['recurrence'].append(f'EXDATE:{exdate_str}')
                            except Exception as ex_e:
                                logger.warning(f"Failed to process EXDATE: {ex_e}")
                        
            except Exception as e:
                logger.warning(f"Failed to convert RRULE for event {event_data.uid}: {e}")
                # 如果週期規則轉換失敗，移除週期性，作為單次事件處理
        
        # 處理參與者
        if event_data.attendees:
            google_event['attendees'] = []
            for attendee in event_data.attendees:
                google_attendee = {
                    'email': attendee['email'].replace('mailto:', ''),
                    'displayName': attendee['name'],
                    'responseStatus': self._convert_attendee_status(attendee['status'])
                }
                google_event['attendees'].append(google_attendee)
        
        # 添加自訂屬性以追蹤原始 UID
        google_event['extendedProperties'] = {
            'private': {
                'originalUID': event_data.uid,
                'originalSequence': str(event_data.sequence),
                'syncFingerprint': event_data.fingerprint
            }
        }
        
        return google_event
    
    def _convert_status(self, ics_status: str) -> str:
        """轉換事件狀態"""
        status_map = {
            'CONFIRMED': 'confirmed',
            'TENTATIVE': 'tentative',
            'CANCELLED': 'cancelled'
        }
        return status_map.get(ics_status.upper(), 'confirmed')
    
    def _convert_attendee_status(self, ics_status: str) -> str:
        """轉換參與者狀態"""
        status_map = {
            'ACCEPTED': 'accepted',
            'DECLINED': 'declined',
            'TENTATIVE': 'tentative',
            'NEEDS-ACTION': 'needsAction'
        }
        return status_map.get(ics_status.upper(), 'needsAction')
    
    def find_events_by_original_uid(self, original_uid: str, 
                                  calendar_id: str = None) -> List[Dict[str, Any]]:
        """根據原始 UID 尋找事件"""
        if not self.service:
            self.authenticate()
        
        calendar_id = calendar_id or self.config.calendar_id
        
        try:
            # 使用私有擴展屬性搜尋
            events_result = self.service.events().list(
                calendarId=calendar_id,
                privateExtendedProperty=f'originalUID={original_uid}',
                maxResults=100
            ).execute()
            
            return events_result.get('items', [])
            
        except HttpError as e:
            logger.error(f"Failed to find events by UID {original_uid}: {e}")
            return []
    
    def _fix_rrule_for_google(self, rrule_str: str) -> Optional[str]:
        """修正 RRULE 格式以符合 Google Calendar 要求"""
        if not rrule_str:
            return None
        
        try:
            # 處理 icalendar vRecur 物件
            if 'vRecur(' in str(rrule_str):
                # 這是 vRecur 物件，需要轉換為標準格式
                return self._convert_vrecur_to_rrule(rrule_str)
            
            # 移除常見的問題格式
            rrule_str = rrule_str.strip()
            
            # 檢查是否包含 Google Calendar 不支援的規則
            unsupported_patterns = [
                'BYSETPOS',  # Google Calendar 不完全支援
                'RSCALE',    # 非標準屬性
                'SKIP',      # 非標準屬性
            ]
            
            for pattern in unsupported_patterns:
                if pattern in rrule_str.upper():
                    logger.warning(f"RRULE contains unsupported pattern {pattern}, skipping recurrence")
                    return None
            
            # 基本驗證 - 確保包含必要的 FREQ
            if 'FREQ=' not in rrule_str.upper():
                logger.warning(f"Invalid RRULE format (no FREQ): {rrule_str}")
                return None
            
            # 限制過於複雜的規則
            if rrule_str.count(';') > 10:  # 過於複雜的規則
                logger.warning(f"RRULE too complex, skipping: {rrule_str}")
                return None
            
            return rrule_str
            
        except Exception as e:
            logger.warning(f"Error processing RRULE: {e}")
            return None
    
    def _convert_vrecur_to_rrule(self, vrecur_obj) -> Optional[str]:
        """將 vRecur 物件轉換為標準 RRULE 字串"""
        try:
            # 如果是字串形式的 vRecur，解析它
            if isinstance(vrecur_obj, str) and 'vRecur(' in vrecur_obj:
                # 嘗試從字串中提取資訊
                import re
                
                # 提取 FREQ
                freq_match = re.search(r"'FREQ':\s*\['(\w+)'\]", str(vrecur_obj))
                if not freq_match:
                    return None
                
                freq = freq_match.group(1)
                rrule_parts = [f"FREQ={freq}"]
                
                # 提取 INTERVAL
                interval_match = re.search(r"'INTERVAL':\s*\[(\d+)\]", str(vrecur_obj))
                if interval_match:
                    rrule_parts.append(f"INTERVAL={interval_match.group(1)}")
                
                # 提取 BYDAY
                byday_match = re.search(r"'BYDAY':\s*\['(\w+)'\]", str(vrecur_obj))
                if byday_match:
                    rrule_parts.append(f"BYDAY={byday_match.group(1)}")
                
                # 提取 BYMONTHDAY
                monthday_match = re.search(r"'BYMONTHDAY':\s*\[(\d+)\]", str(vrecur_obj))
                if monthday_match:
                    rrule_parts.append(f"BYMONTHDAY={monthday_match.group(1)}")
                
                # 提取 UNTIL（需要格式化日期）
                until_match = re.search(r"'UNTIL':\s*\[datetime\.datetime\(([^)]+)\)\]", str(vrecur_obj))
                if until_match:
                    try:
                        # 解析 datetime 參數
                        datetime_args = until_match.group(1)
                        # 嘗試提取年、月、日、時、分
                        parts = [part.strip() for part in datetime_args.split(',')]
                        
                        if len(parts) >= 5:  # 至少有年月日時分
                            year = int(parts[0])
                            month = int(parts[1])
                            day = int(parts[2])
                            hour = int(parts[3])
                            minute = int(parts[4])
                            
                            # 格式化為 Google Calendar 接受的 UTC 時間格式
                            until_str = f"{year:04d}{month:02d}{day:02d}T{hour:02d}{minute:02d}00Z"
                            rrule_parts.append(f"UNTIL={until_str}")
                            logger.debug(f"Added UNTIL to RRULE: {until_str}")
                        else:
                            logger.warning("Could not parse UNTIL datetime, skipping")
                    except Exception as e:
                        logger.warning(f"Error parsing UNTIL date: {e}, skipping")
                
                if len(rrule_parts) > 1:  # 至少有 FREQ 和其他參數
                    return ";".join(rrule_parts)
                else:
                    return f"FREQ={freq}"  # 只有基本頻率
            
            # 如果有 to_ical 方法，使用它
            elif hasattr(vrecur_obj, 'to_ical'):
                return vrecur_obj.to_ical().decode('utf-8')
            
            # 其他情況，返回 None
            return None
            
        except Exception as e:
            logger.warning(f"Failed to convert vRecur to RRULE: {e}")
            return None