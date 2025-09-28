#!/usr/bin/env python3
"""
Calendar Sync Tool
同步公司 ICS 行事曆到 Google Calendar
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

# 添加 src 到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from sync.engine import SyncEngine
from utils.config import load_config
from utils.logger import setup_logging


async def main():
    parser = argparse.ArgumentParser(description="Calendar Sync Tool")
    parser.add_argument("--config", "-c", default="config/settings.yaml",
                       help="Configuration file path")
    parser.add_argument("--once", action="store_true",
                       help="Run sync once and exit")
    parser.add_argument("--force", action="store_true",
                       help="Force full sync (ignore cache)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be synced without making changes")
    
    args = parser.parse_args()
    
    # 載入設定
    config = load_config(args.config)
    
    # 設定日誌
    setup_logging(config.logging)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Calendar Sync Tool")
    logger.info(f"Config file: {args.config}")
    
    try:
        # 建立同步引擎
        sync_engine = SyncEngine(config)
        
        if args.once:
            # 執行一次同步
            logger.info("Running one-time sync")
            await sync_engine.sync_once(force=args.force, dry_run=args.dry_run)
        else:
            # 持續同步模式
            logger.info(f"Starting continuous sync (interval: {config.sync.interval_minutes} minutes)")
            await sync_engine.start_continuous_sync()
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("Calendar Sync Tool stopped")


if __name__ == "__main__":
    asyncio.run(main())