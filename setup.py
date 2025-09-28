#!/usr/bin/env python3
"""
Calendar Sync Tool 安裝和設置腳本
"""
import os
import sys
import json
from pathlib import Path


def check_python_version():
    """檢查 Python 版本"""
    if sys.version_info < (3, 8):
        print("錯誤: 需要 Python 3.8 或更高版本")
        sys.exit(1)
    print(f"✓ Python 版本: {sys.version}")


def setup_directories():
    """建立必要的目錄"""
    directories = ["config", "data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 建立目錄: {directory}")


def check_credentials():
    """檢查 Google API 認證檔案"""
    credentials_file = Path("config/credentials.json")
    
    if not credentials_file.exists():
        print("\n⚠️  Google API 認證檔案不存在")
        print("請按照以下步驟設置:")
        print("1. 前往 Google Cloud Console: https://console.cloud.google.com/")
        print("2. 建立專案並啟用 Google Calendar API")
        print("3. 建立 OAuth 2.0 認證 (Desktop application)")
        print("4. 下載認證檔案並儲存為: config/credentials.json")
        print("\n詳細說明請參考 README.md")
        return False
    
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        if 'installed' in creds and 'client_id' in creds['installed']:
            print("✓ Google API 認證檔案存在且格式正確")
            return True
        else:
            print("⚠️  認證檔案格式不正確")
            return False
            
    except Exception as e:
        print(f"⚠️  認證檔案讀取失敗: {e}")
        return False


def check_config():
    """檢查設定檔案"""
    config_file = Path("config/settings.yaml")
    
    if not config_file.exists():
        print("⚠️  設定檔案不存在，將使用預設設定")
        return False
    
    print("✓ 設定檔案存在")
    return True


def test_imports():
    """測試 Python 套件導入"""
    print("\n檢查 Python 套件...")
    
    required_packages = [
        'icalendar',
        'google.oauth2',
        'googleapiclient',
        'requests',
        'pytz',
        'recurring_ical_events',
        'pydantic',
        'yaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 缺少")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少套件，請執行: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """主要安裝程序"""
    print("Calendar Sync Tool 安裝檢查")
    print("=" * 40)
    
    # 檢查 Python 版本
    check_python_version()
    
    # 建立目錄
    print("\n建立目錄...")
    setup_directories()
    
    # 檢查套件
    if not test_imports():
        print("\n請先安裝必要的套件:")
        print("pip install -r requirements.txt")
        return
    
    # 檢查設定
    print("\n檢查設定...")
    config_ok = check_config()
    creds_ok = check_credentials()
    
    print("\n" + "=" * 40)
    
    if config_ok and creds_ok:
        print("✅ 安裝檢查完成！可以開始使用。")
        print("\n建議的下一步:")
        print("1. 測試基本功能: python test_basic.py")
        print("2. 乾跑測試: python main.py --once --dry-run")
        print("3. 執行同步: python main.py --once")
    else:
        print("⚠️  安裝未完成，請解決上述問題後重新執行。")
        
        if not creds_ok:
            print("\n需要設置 Google API 認證")
        if not config_ok:
            print("\n需要調整設定檔案")


if __name__ == "__main__":
    main()