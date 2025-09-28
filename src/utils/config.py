"""
設定管理模組
"""
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class SourceConfig(BaseModel):
    """源 ICS 設定"""
    url: str
    timeout: int = 30
    retry_count: int = 3
    user_agent: str = "Calendar-Sync/1.0"


class GoogleCalendarConfig(BaseModel):
    """Google Calendar 設定"""
    calendar_id: str = "primary"
    credentials_file: str = "config/credentials.json"
    token_file: str = "config/token.json"
    application_name: str = "CalendarBridge"
    auth_type: str = "oauth"  # "oauth" 或 "service_account"
    service_account_file: str = "config/service_account.json"


class SyncConfig(BaseModel):
    """同步設定"""
    interval_minutes: int = 30
    max_events_per_batch: int = 100
    lookahead_days: int = 365
    lookbehind_days: int = 30
    enable_delete: bool = True
    conflict_resolution: str = "latest"


class DatabaseConfig(BaseModel):
    """資料庫設定"""
    path: str = "data/sync_state.db"
    backup_count: int = 5


class LoggingConfig(BaseModel):
    """日誌設定"""
    level: str = "INFO"
    file: str = "logs/calendarbridge.log"
    max_size_mb: int = 10
    backup_count: int = 5
    console: bool = True


class ProcessingConfig(BaseModel):
    """事件處理設定"""
    timezone: str = "Asia/Taipei"
    event_prefix: str = "[ITRI] "
    description_suffix: str = "\n\n--- 由 Calendar Sync 工具同步 ---"
    max_description_length: int = 8000


class Config(BaseSettings):
    """主設定類別"""
    source: SourceConfig
    google_calendar: GoogleCalendarConfig
    sync: SyncConfig
    database: DatabaseConfig
    logging: LoggingConfig
    processing: ProcessingConfig
    
    class Config:
        env_nested_delimiter = '__'


def load_config(config_path: str) -> Config:
    """載入設定檔案"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    return Config(**config_data)