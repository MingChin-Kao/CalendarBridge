"""
日誌設定模組
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from src.utils.config import LoggingConfig


def setup_logging(config: LoggingConfig) -> None:
    """設定日誌系統"""
    
    # 建立日誌目錄
    log_file = Path(config.file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 設定根日誌器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))
    
    # 清除現有處理器
    root_logger.handlers.clear()
    
    # 建立格式器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 檔案處理器 (使用 RotatingFileHandler)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=config.max_size_mb * 1024 * 1024,  # 轉換為位元組
        backupCount=config.backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 控制台處理器 (如果啟用)
    if config.console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 設定第三方套件的日誌級別
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    logging.getLogger('google_auth_httplib2').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)