#!/usr/bin/env python3
"""
清理 Google Calendar 腳本 - 刪除所有已同步的事件
警告：此腳本會直接刪除事件，不會提示確認
"""
import sys
from pathlib import Path

# 添加 src 到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config

def main():
    print("開始清理 Google Calendar 事件...")

    try:
        # 載入設定
        config = load_config("config/settings.yaml")

        # 建立 Google Calendar 客戶端
        client = GoogleCalendarClient(config.google_calendar)
        client.authenticate()

        # 取得日曆資訊
        calendar_info = client.get_calendar_info()
        print(f"目標日曆: {calendar_info.get('summary', 'Unknown')}")

        # 列出所有事件
        print("正在獲取所有事件...")
        events = client.service.events().list(
            calendarId=config.google_calendar.calendar_id,
            maxResults=2500,
            singleEvents=False  # 包含週期事件
        ).execute()

        items = events.get('items', [])
        print(f"找到 {len(items)} 個事件")

        if not items:
            print("沒有事件需要清理")
            return

        # 刪除所有事件
        deleted_count = 0
        failed_count = 0

        for event in items:
            event_id = event.get('id')
            summary = event.get('summary', '(無標題)')

            try:
                client.service.events().delete(
                    calendarId=config.google_calendar.calendar_id,
                    eventId=event_id
                ).execute()
                deleted_count += 1
                print(f"✓ 已刪除: {summary} (ID: {event_id})")

            except Exception as e:
                failed_count += 1
                print(f"✗ 刪除失敗: {summary} (ID: {event_id}) - {e}")

        print(f"\n清理完成:")
        print(f"  - 成功刪除: {deleted_count} 個事件")
        print(f"  - 刪除失敗: {failed_count} 個事件")

    except Exception as e:
        print(f"❌ 清理失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
