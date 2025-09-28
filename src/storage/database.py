"""
本地狀態管理資料庫
用於追蹤同步狀態、事件變更和映射關係
"""
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from contextlib import contextmanager

from src.utils.config import DatabaseConfig
from src.parsers.ics_parser import EventData


logger = logging.getLogger(__name__)


class SyncDatabase:
    """同步狀態資料庫"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.db_path = Path(config.path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化資料庫結構"""
        with self._get_connection() as conn:
            # 事件快照表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS event_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_uid TEXT NOT NULL,
                    series_uid TEXT,  -- 週期事件系列ID
                    sequence INTEGER NOT NULL DEFAULT 0,
                    fingerprint TEXT NOT NULL,
                    event_data TEXT NOT NULL,  -- JSON 格式的事件資料
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(original_uid)
                )
            ''')
            
            # Google Calendar 事件映射表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS event_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_uid TEXT NOT NULL,
                    google_event_id TEXT NOT NULL,
                    google_calendar_id TEXT NOT NULL,
                    last_sync_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sync_status TEXT DEFAULT 'synced',  -- synced, pending, failed
                    error_message TEXT,
                    UNIQUE(original_uid, google_calendar_id)
                )
            ''')
            
            # 同步歷史表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_started_at TIMESTAMP,
                    sync_completed_at TIMESTAMP,
                    events_processed INTEGER DEFAULT 0,
                    events_created INTEGER DEFAULT 0,
                    events_updated INTEGER DEFAULT 0,
                    events_deleted INTEGER DEFAULT 0,
                    errors_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'running',  -- running, completed, failed
                    error_message TEXT
                )
            ''')
            
            # 建立索引
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_snapshots_uid ON event_snapshots(original_uid)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_mappings_uid ON event_mappings(original_uid)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_mappings_google_id ON event_mappings(google_event_id)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def _get_connection(self):
        """取得資料庫連線的 context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 允許使用欄位名稱存取
        try:
            yield conn
        finally:
            conn.close()
    
    def save_event_snapshot(self, event_data: EventData) -> None:
        """儲存事件快照"""
        with self._get_connection() as conn:
            event_json = json.dumps(event_data.to_dict(), ensure_ascii=False)
            
            # 使用唯一事件ID作為索引
            unique_id = event_data.get_unique_event_id()
            series_id = event_data.get_series_id() if event_data.is_recurring() else None
            
            conn.execute('''
                INSERT OR REPLACE INTO event_snapshots 
                (original_uid, series_uid, sequence, fingerprint, event_data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                unique_id,
                series_id,
                event_data.sequence,
                event_data.fingerprint,
                event_json,
                datetime.now().isoformat()
            ))
            conn.commit()
    
    def get_event_snapshot(self, original_uid: str) -> Optional[Dict[str, Any]]:
        """取得事件快照"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM event_snapshots WHERE original_uid = ?',
                (original_uid,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'original_uid': row['original_uid'],
                    'sequence': row['sequence'],
                    'fingerprint': row['fingerprint'],
                    'event_data': json.loads(row['event_data']),
                    'updated_at': row['updated_at']
                }
            return None
    
    def get_all_event_snapshots(self) -> List[Dict[str, Any]]:
        """取得所有事件快照"""
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM event_snapshots ORDER BY updated_at DESC')
            rows = cursor.fetchall()
            
            return [
                {
                    'original_uid': row['original_uid'],
                    'sequence': row['sequence'],
                    'fingerprint': row['fingerprint'],
                    'event_data': json.loads(row['event_data']),
                    'updated_at': row['updated_at']
                }
                for row in rows
            ]
    
    def save_event_mapping(self, original_uid: str, google_event_id: str, 
                          google_calendar_id: str, sync_status: str = 'synced') -> None:
        """儲存事件映射"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO event_mappings 
                (original_uid, google_event_id, google_calendar_id, last_sync_at, sync_status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                original_uid,
                google_event_id,
                google_calendar_id,
                datetime.now().isoformat(),
                sync_status
            ))
            conn.commit()
    
    def get_event_mapping(self, original_uid: str, 
                         google_calendar_id: str) -> Optional[Dict[str, Any]]:
        """取得事件映射"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM event_mappings 
                WHERE original_uid = ? AND google_calendar_id = ?
            ''', (original_uid, google_calendar_id))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_all_event_mappings(self, google_calendar_id: str) -> List[Dict[str, Any]]:
        """取得指定行事曆的所有事件映射"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM event_mappings 
                WHERE google_calendar_id = ? 
                ORDER BY last_sync_at DESC
            ''', (google_calendar_id,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def delete_event_mapping(self, original_uid: str, google_calendar_id: str) -> None:
        """刪除事件映射"""
        with self._get_connection() as conn:
            conn.execute('''
                DELETE FROM event_mappings 
                WHERE original_uid = ? AND google_calendar_id = ?
            ''', (original_uid, google_calendar_id))
            conn.commit()
    
    def delete_event_mapping_by_google_id(self, google_event_id: str, google_calendar_id: str) -> None:
        """根據 Google Event ID 刪除事件映射"""
        with self._get_connection() as conn:
            conn.execute('''
                DELETE FROM event_mappings 
                WHERE google_event_id = ? AND google_calendar_id = ?
            ''', (google_event_id, google_calendar_id))
            conn.commit()
    
    def start_sync_session(self) -> int:
        """開始同步會話，返回會話 ID"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO sync_history (sync_started_at, status)
                VALUES (?, ?)
            ''', (datetime.now().isoformat(), 'running'))
            conn.commit()
            return cursor.lastrowid
    
    def update_sync_session(self, session_id: int, **kwargs) -> None:
        """更新同步會話"""
        if not kwargs:
            return
        
        # 建立動態 SQL
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['events_processed', 'events_created', 'events_updated', 
                      'events_deleted', 'errors_count', 'status', 'error_message']:
                set_clauses.append(f'{key} = ?')
                values.append(value)
        
        if 'status' in kwargs and kwargs['status'] in ['completed', 'failed']:
            set_clauses.append('sync_completed_at = ?')
            values.append(datetime.now().isoformat())
        
        if set_clauses:
            values.append(session_id)
            sql = f'UPDATE sync_history SET {", ".join(set_clauses)} WHERE id = ?'
            
            with self._get_connection() as conn:
                conn.execute(sql, values)
                conn.commit()
    
    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """取得同步歷史"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM sync_history 
                ORDER BY sync_started_at DESC 
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def detect_changes(self, current_events: List[EventData]) -> Tuple[List[EventData], List[EventData], List[str]]:
        """
        偵測事件變更
        返回: (新事件列表, 更新事件列表, 刪除事件 UID 列表)
        """
        new_events = []
        updated_events = []
        
        # 建立當前事件的唯一ID集合
        current_unique_ids = {event.get_unique_event_id() for event in current_events}
        
        # 取得所有現有快照
        existing_snapshots = {
            snapshot['original_uid']: snapshot 
            for snapshot in self.get_all_event_snapshots()
        }
        existing_unique_ids = set(existing_snapshots.keys())
        
        # 檢查每個當前事件
        for event in current_events:
            unique_id = event.get_unique_event_id()
            
            if unique_id not in existing_snapshots:
                # 新事件
                new_events.append(event)
            else:
                # 檢查是否有變更
                snapshot = existing_snapshots[unique_id]
                if (event.sequence > snapshot['sequence'] or 
                    event.fingerprint != snapshot['fingerprint']):
                    updated_events.append(event)
        
        # 找出已刪除的事件
        deleted_uids = list(existing_unique_ids - current_unique_ids)
        
        logger.info(f"Change detection: {len(new_events)} new, {len(updated_events)} updated, {len(deleted_uids)} deleted")
        
        return new_events, updated_events, deleted_uids
    
    def get_orphaned_series_events(self, current_events: List[EventData]) -> List[str]:
        """檢測週期事件系列變更後的孤兒事件"""
        orphaned_uids = []
        
        # 建立當前週期事件系列的映射
        current_series = {}
        for event in current_events:
            if event.is_recurring():
                series_id = event.get_series_id()
                if series_id not in current_series:
                    current_series[series_id] = []
                current_series[series_id].append(event.get_unique_event_id())
        
        with self._get_connection() as conn:
            # 查找所有已知的週期事件系列
            cursor = conn.execute('''
                SELECT DISTINCT series_uid FROM event_snapshots 
                WHERE series_uid IS NOT NULL
            ''')
            
            for row in cursor.fetchall():
                series_uid = row[0]
                
                if series_uid in current_series:
                    # 檢查這個系列是否有孤兒事件
                    current_uids = set(current_series[series_uid])
                    
                    # 查找資料庫中這個系列的所有事件
                    series_cursor = conn.execute('''
                        SELECT original_uid FROM event_snapshots 
                        WHERE series_uid = ?
                    ''', (series_uid,))
                    
                    existing_uids = {row[0] for row in series_cursor.fetchall()}
                    
                    # 找出孤兒事件
                    orphans = existing_uids - current_uids
                    orphaned_uids.extend(orphans)
                else:
                    # 整個系列已不存在，所有事件都是孤兒
                    series_cursor = conn.execute('''
                        SELECT original_uid FROM event_snapshots 
                        WHERE series_uid = ?
                    ''', (series_uid,))
                    
                    orphaned_uids.extend([row[0] for row in series_cursor.fetchall()])
        
        if orphaned_uids:
            logger.info(f"Found {len(orphaned_uids)} orphaned recurring event instances")
        
        return orphaned_uids
    
    def cleanup_old_data(self, days: int = 90) -> None:
        """清理舊資料"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            # 清理舊的同步歷史
            cursor = conn.execute(
                'DELETE FROM sync_history WHERE sync_started_at < ?',
                (cutoff_date,)
            )
            deleted_history = cursor.rowcount
            
            conn.commit()
            
            if deleted_history > 0:
                logger.info(f"Cleaned up {deleted_history} old sync history records")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """取得資料庫統計資訊"""
        with self._get_connection() as conn:
            stats = {}
            
            # 事件快照數量
            cursor = conn.execute('SELECT COUNT(*) FROM event_snapshots')
            stats['event_snapshots_count'] = cursor.fetchone()[0]
            
            # 事件映射數量
            cursor = conn.execute('SELECT COUNT(*) FROM event_mappings')
            stats['event_mappings_count'] = cursor.fetchone()[0]
            
            # 同步歷史數量
            cursor = conn.execute('SELECT COUNT(*) FROM sync_history')
            stats['sync_history_count'] = cursor.fetchone()[0]
            
            # 最後同步時間
            cursor = conn.execute('''
                SELECT sync_started_at FROM sync_history 
                WHERE status = 'completed' 
                ORDER BY sync_started_at DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            stats['last_successful_sync'] = row[0] if row else None
            
            return stats
    
    def backup_database(self, backup_path: Optional[Path] = None) -> Path:
        """備份資料庫"""
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.db_path.parent / f"sync_state_backup_{timestamp}.db"
        
        with self._get_connection() as source_conn:
            backup_conn = sqlite3.connect(backup_path)
            source_conn.backup(backup_conn)
            backup_conn.close()
        
        logger.info(f"Database backed up to: {backup_path}")
        return backup_path