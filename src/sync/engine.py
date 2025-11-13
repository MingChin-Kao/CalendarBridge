"""
同步引擎
負責協調 ICS 解析、Google Calendar 操作和狀態管理
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from zoneinfo import ZoneInfo

from src.parsers.ics_parser import ICSParser, EventData
from src.clients.google_calendar import GoogleCalendarClient
from src.storage.database import SyncDatabase
from src.utils.config import Config


logger = logging.getLogger(__name__)


class SyncEngine:
    """同步引擎主類別"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # 初始化組件
        self.ics_parser = ICSParser(config.source, config.processing)
        self.google_client = GoogleCalendarClient(config.google_calendar)
        self.database = SyncDatabase(config.database)
        
        # 同步狀態
        self.is_running = False
        self.current_session_id = None
    
    async def sync_once(self, force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """執行一次同步"""
        logger.info(f"Starting sync (force={force}, dry_run={dry_run})")
        
        # 開始同步會話
        session_id = self.database.start_sync_session()
        self.current_session_id = session_id
        
        stats = {
            'events_processed': 0,
            'events_created': 0,
            'events_updated': 0,
            'events_deleted': 0,
            'errors_count': 0
        }
        
        try:
            # 1. 認證 Google Calendar
            if not dry_run:
                self.google_client.authenticate()
                calendar_info = self.google_client.get_calendar_info()
                logger.info(f"Target calendar: {calendar_info.get('summary', 'Unknown')}")
            
            # 2. 計算同步時間範圍
            now = datetime.now(ZoneInfo(self.config.processing.timezone))
            start_date = now - timedelta(days=self.config.sync.lookbehind_days)
            end_date = now + timedelta(days=self.config.sync.lookahead_days)
            
            logger.info(f"Sync range: {start_date.date()} to {end_date.date()}")
            
            # 3. 解析和展開 ICS 事件
            logger.info("Fetching and parsing ICS events...")
            current_events, modified_instances = self.ics_parser.parse_and_expand(start_date, end_date)
            stats['events_processed'] = len(current_events)

            # 4. 偵測變更
            logger.info("Detecting changes...")
            new_events, updated_events, deleted_uids = self.database.detect_changes(current_events)

            # 4.3 處理修改的週期實例 - 需要刪除原始日期上的舊實例
            modified_instance_cleanups = self._detect_modified_instance_cleanups(modified_instances)
            if modified_instance_cleanups:
                logger.info(f"Found {len(modified_instance_cleanups)} modified recurring instances that need cleanup")
                deleted_uids.extend(modified_instance_cleanups)

            # 4.5 偵測週期事件系列的孤兒事件
            orphaned_uids = self.database.get_orphaned_series_events(current_events)
            if orphaned_uids:
                deleted_uids.extend(orphaned_uids)
            
            # 5. 執行同步操作
            if not dry_run:
                # 處理新事件
                if new_events:
                    logger.info(f"Creating {len(new_events)} new events...")
                    created_count = await self._create_events(new_events)
                    stats['events_created'] = created_count
                
                # 處理更新事件
                if updated_events:
                    logger.info(f"Updating {len(updated_events)} events...")
                    updated_count = await self._update_events(updated_events)
                    stats['events_updated'] = updated_count
                
                # 處理刪除事件
                if deleted_uids and self.config.sync.enable_delete:
                    logger.info(f"Deleting {len(deleted_uids)} events...")
                    deleted_count = await self._delete_events(deleted_uids)
                    stats['events_deleted'] = deleted_count
                
                # 更新事件快照
                logger.info("Updating event snapshots...")
                for event in current_events:
                    self.database.save_event_snapshot(event)
                
            else:
                # Dry run - 只顯示會做什麼
                logger.info("DRY RUN - Would perform the following actions:")
                logger.info(f"  Create {len(new_events)} new events")
                logger.info(f"  Update {len(updated_events)} events")
                logger.info(f"  Delete {len(deleted_uids)} events")
                
                for event in new_events[:5]:  # 顯示前5個新事件
                    logger.info(f"    NEW: {event.summary} ({event.start_datetime})")
                
                for event in updated_events[:5]:  # 顯示前5個更新事件
                    logger.info(f"    UPDATE: {event.summary} ({event.start_datetime})")
                
                for uid in deleted_uids[:5]:  # 顯示前5個刪除事件
                    logger.info(f"    DELETE: {uid}")
            
            # 更新同步會話狀態
            self.database.update_sync_session(
                session_id,
                status='completed',
                **stats
            )
            
            logger.info(f"Sync completed successfully: {stats}")
            return stats
            
        except Exception as e:
            # 記錄錯誤
            error_message = str(e)
            logger.error(f"Sync failed: {error_message}", exc_info=True)
            
            stats['errors_count'] = 1
            self.database.update_sync_session(
                session_id,
                status='failed',
                error_message=error_message,
                **stats
            )
            
            raise
        
        finally:
            self.current_session_id = None
    
    async def start_continuous_sync(self) -> None:
        """開始持續同步模式"""
        self.is_running = True
        logger.info(f"Starting continuous sync (interval: {self.config.sync.interval_minutes} minutes)")
        
        while self.is_running:
            try:
                await self.sync_once()
                
                # 等待下次同步
                if self.is_running:
                    await asyncio.sleep(self.config.sync.interval_minutes * 60)
                    
            except Exception as e:
                logger.error(f"Error in continuous sync: {e}")
                # 等待較短時間後重試
                if self.is_running:
                    await asyncio.sleep(300)  # 5分鐘後重試
    
    def stop_continuous_sync(self) -> None:
        """停止持續同步"""
        logger.info("Stopping continuous sync...")
        self.is_running = False
    
    async def _create_events(self, events: List[EventData]) -> int:
        """建立新事件"""
        created_count = 0
        
        for event in events:
            try:
                # 建立 Google Calendar 事件
                google_event = self.google_client.create_event(event)
                
                # 儲存映射關係
                unique_id = event.get_unique_event_id()
                self.database.save_event_mapping(
                    unique_id,
                    google_event['id'],
                    self.config.google_calendar.calendar_id
                )
                
                created_count += 1
                
            except Exception as e:
                logger.error(f"Failed to create event {event.uid}: {e}")
                continue
        
        return created_count
    
    async def _update_events(self, events: List[EventData]) -> int:
        """更新事件"""
        updated_count = 0
        
        for event in events:
            try:
                # 查找 Google Calendar 事件 ID
                unique_id = event.get_unique_event_id()
                mapping = self.database.get_event_mapping(
                    unique_id, 
                    self.config.google_calendar.calendar_id
                )
                
                if mapping:
                    # 更新現有事件
                    google_event = self.google_client.update_event(
                        mapping['google_event_id'],
                        event
                    )
                    
                    # 更新映射的同步時間
                    self.database.save_event_mapping(
                        unique_id,
                        mapping['google_event_id'],
                        self.config.google_calendar.calendar_id
                    )
                    
                    updated_count += 1
                    
                else:
                    # 如果找不到映射，嘗試搜尋 Google Calendar
                    google_events = self.google_client.find_events_by_original_uid(event.uid)
                    
                    if google_events:
                        # 找到對應事件，更新並建立映射
                        google_event = self.google_client.update_event(
                            google_events[0]['id'],
                            event
                        )
                        
                        self.database.save_event_mapping(
                            unique_id,
                            google_events[0]['id'],
                            self.config.google_calendar.calendar_id
                        )
                        
                        updated_count += 1
                        
                    else:
                        # 找不到對應事件，建立新事件
                        logger.warning(f"Event {unique_id} not found in Google Calendar, creating new")
                        google_event = self.google_client.create_event(event)
                        
                        self.database.save_event_mapping(
                            unique_id,
                            google_event['id'],
                            self.config.google_calendar.calendar_id
                        )
                        
                        updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update event {event.uid}: {e}")
                continue
        
        return updated_count
    
    async def _delete_events(self, deleted_uids: List[str]) -> int:
        """刪除事件"""
        deleted_count = 0
        
        for uid in deleted_uids:
            try:
                # 查找 Google Calendar 事件 ID
                mapping = self.database.get_event_mapping(
                    uid, 
                    self.config.google_calendar.calendar_id
                )
                
                if mapping:
                    # 刪除 Google Calendar 事件
                    self.google_client.delete_event(mapping['google_event_id'])
                    
                    # 刪除映射關係
                    self.database.delete_event_mapping(
                        uid,
                        self.config.google_calendar.calendar_id
                    )
                    
                    deleted_count += 1
                    
                else:
                    logger.warning(f"No mapping found for deleted event {uid}")
                
                # 刪除事件快照（無論是否有映射）
                # 這個操作需要在 database.py 中添加相應方法
                
            except Exception as e:
                logger.error(f"Failed to delete event {uid}: {e}")
                continue
        
        return deleted_count
    
    def get_sync_status(self) -> Dict[str, Any]:
        """取得同步狀態"""
        db_stats = self.database.get_database_stats()
        
        status = {
            'is_running': self.is_running,
            'current_session_id': self.current_session_id,
            'database_stats': db_stats,
            'config': {
                'source_url': self.config.source.url,
                'calendar_id': self.config.google_calendar.calendar_id,
                'sync_interval_minutes': self.config.sync.interval_minutes,
                'enable_delete': self.config.sync.enable_delete
            }
        }
        
        return status
    
    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得同步歷史"""
        return self.database.get_sync_history(limit)

    def _detect_modified_instance_cleanups(self, modified_instances: List[EventData]) -> List[str]:
        """
        偵測修改的週期實例，並返回需要清理的原始事件 UID

        注意：在理想情況下，當週期事件的 EXDATE 被更新後，
        Google Calendar 應該會自動隱藏被排除的日期。

        但如果 EXDATE 沒有正確生效，這個方法會檢測是否有需要手動清理的事件。
        目前這個方法返回空列表，因為主要修復是在 EXDATE 的格式上。
        """
        # 目前不需要特殊的清理邏輯
        # EXDATE 的修復應該能解決問題
        return []