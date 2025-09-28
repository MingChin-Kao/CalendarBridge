#!/usr/bin/env python3
"""
取得 Google Calendar 行事曆列表
幫助您找到要同步的目標行事曆 ID
"""
import sys
from pathlib import Path

# 添加 src 到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config
import logging

def main():
    try:
        # 載入設定
        config = load_config("config/settings.yaml")
        
        # 建立 Google Calendar 客戶端
        client = GoogleCalendarClient(config.google_calendar)
        
        # 認證
        print("正在認證 Google Calendar...")
        client.authenticate()
        
        # 取得行事曆列表
        print("\n您的 Google Calendar 行事曆列表：")
        print("=" * 50)
        
        calendar_list = client.service.calendarList().list().execute()
        
        for i, calendar in enumerate(calendar_list.get('items', []), 1):
            calendar_id = calendar['id']
            summary = calendar.get('summary', '未命名')
            access_role = calendar.get('accessRole', 'unknown')
            primary = " (主要)" if calendar.get('primary', False) else ""
            
            print(f"{i}. {summary}{primary}")
            print(f"   ID: {calendar_id}")
            print(f"   權限: {access_role}")
            print()
        
        print("使用方法：")
        print("1. 選擇要同步的行事曆")
        print("2. 複製對應的 ID")
        print("3. 在 config/settings.yaml 中修改 calendar_id")
        print("\n例如：")
        print("google_calendar:")
        print("  calendar_id: \"您選擇的行事曆ID\"")
        
    except FileNotFoundError:
        print("❌ 找不到 Google API 認證檔案")
        print("請先設置 config/credentials.json")
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    main()