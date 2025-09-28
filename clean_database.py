#!/usr/bin/env python3
"""
清理資料庫腳本 - 重置同步狀態
"""
import sys
from pathlib import Path

# 添加 src 到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from src.storage.database import SyncDatabase
from src.utils.config import load_config

def main():
    print("清理同步資料庫...")
    
    try:
        # 載入設定
        config = load_config("config/settings.yaml")
        
        # 建立資料庫連線
        database = SyncDatabase(config.database)
        
        # 清理所有資料
        with database._get_connection() as conn:
            # 清除事件快照
            cursor = conn.execute("DELETE FROM event_snapshots")
            snapshots_deleted = cursor.rowcount
            
            # 清除事件映射
            cursor = conn.execute("DELETE FROM event_mappings")
            mappings_deleted = cursor.rowcount
            
            # 清除同步歷史（保留最近5次）
            cursor = conn.execute("""
                DELETE FROM sync_history 
                WHERE id NOT IN (
                    SELECT id FROM sync_history 
                    ORDER BY sync_started_at DESC 
                    LIMIT 5
                )
            """)
            history_deleted = cursor.rowcount
            
            conn.commit()
        
        print(f"✅ 清理完成:")
        print(f"   - 刪除 {snapshots_deleted} 個事件快照")
        print(f"   - 刪除 {mappings_deleted} 個事件映射")
        print(f"   - 刪除 {history_deleted} 個舊同步記錄")
        print("\n現在可以重新執行同步以避免重複事件問題。")
        
    except Exception as e:
        print(f"❌ 清理失敗: {e}")

if __name__ == "__main__":
    main()