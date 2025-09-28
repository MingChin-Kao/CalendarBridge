#!/usr/bin/env python3
"""
顯示同步狀態 - 查看資料庫中記錄的事件
"""
import sys
from pathlib import Path
import json

# 添加 src 到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from src.storage.database import SyncDatabase
from src.utils.config import load_config

def main():
    try:
        # 載入設定
        config = load_config("config/settings.yaml")
        database = SyncDatabase(config.database)
        
        print("=== 同步狀態報告 ===\n")
        
        # 取得資料庫統計
        stats = database.get_database_stats()
        print("📊 資料庫統計:")
        print(f"   事件快照數量: {stats['event_snapshots_count']}")
        print(f"   事件映射數量: {stats['event_mappings_count']}")
        print(f"   同步歷史記錄: {stats['sync_history_count']}")
        print(f"   最後成功同步: {stats['last_successful_sync']}")
        
        print("\n📋 前10個已同步事件:")
        print("-" * 80)
        
        # 取得事件快照
        snapshots = database.get_all_event_snapshots()[:10]
        
        for i, snapshot in enumerate(snapshots, 1):
            event_data = snapshot['event_data']
            print(f"{i}. 唯一ID: {snapshot['original_uid'][:50]}...")
            print(f"   標題: {event_data['summary']}")
            print(f"   時間: {event_data['start_datetime']}")
            print(f"   指紋: {snapshot['fingerprint'][:16]}...")
            print(f"   更新: {snapshot['updated_at']}")
            print()
        
        print("🗂️ Google Calendar 映射 (前5個):")
        print("-" * 60)
        
        # 取得映射關係
        mappings = database.get_all_event_mappings(config.google_calendar.calendar_id)[:5]
        
        for i, mapping in enumerate(mappings, 1):
            print(f"{i}. 原始ID: {mapping['original_uid'][:50]}...")
            print(f"   Google ID: {mapping['google_event_id']}")
            print(f"   同步時間: {mapping['last_sync_at']}")
            print()
        
        print("🔍 變更檢測示例:")
        print("當程式再次執行時，會比對:")
        print("1. 每個事件的唯一ID是否在 event_snapshots 中存在")
        print("2. 如果存在，比對 fingerprint 是否改變")
        print("3. 如果改變，標記為需要更新")
        print("4. 通過 event_mappings 找到對應的 Google 事件進行更新")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    main()