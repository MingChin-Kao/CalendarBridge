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


def check_credentials(auth_type="oauth"):
    """檢查 Google API 認證檔案

    Args:
        auth_type: 認證類型 ("oauth" 或 "service_account")
    """
    if auth_type == "service_account":
        # 檢查服務帳號金鑰檔案
        service_account_file = Path("config/service_account.json")

        if not service_account_file.exists():
            print("\n⚠️  服務帳號金鑰檔案不存在")
            print("請按照以下步驟設置:")
            print("1. 前往 Google Cloud Console: https://console.cloud.google.com/")
            print("2. 建立專案並啟用 Google Calendar API")
            print("3. 建立服務帳號並下載 JSON 金鑰檔案")
            print("4. 將金鑰檔案儲存為: config/service_account.json")
            print("5. 將目標行事曆分享給服務帳號的 email")
            print("\n詳細說明請參考: docs/service_account_setup.md")
            return False

        try:
            with open(service_account_file, 'r') as f:
                creds = json.load(f)

            if 'type' in creds and creds['type'] == 'service_account' and 'client_email' in creds:
                print(f"✓ 服務帳號金鑰檔案存在且格式正確")
                print(f"  服務帳號 email: {creds['client_email']}")
                return True
            else:
                print("⚠️  服務帳號金鑰檔案格式不正確")
                return False

        except Exception as e:
            print(f"⚠️  服務帳號金鑰檔案讀取失敗: {e}")
            return False

    else:  # OAuth
        credentials_file = Path("config/credentials.json")

        if not credentials_file.exists():
            print("\n⚠️  OAuth 認證檔案不存在")
            print("請按照以下步驟設置:")
            print("1. 前往 Google Cloud Console: https://console.cloud.google.com/")
            print("2. 建立專案並啟用 Google Calendar API")
            print("3. 建立 OAuth 2.0 認證 (Desktop application)")
            print("4. 下載認證檔案並儲存為: config/credentials.json")
            print("\n詳細說明請參考: docs/google_api_setup.md")
            return False

        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)

            if 'installed' in creds and 'client_id' in creds['installed']:
                print("✓ OAuth 認證檔案存在且格式正確")
                return True
            else:
                print("⚠️  OAuth 認證檔案格式不正確")
                return False

        except Exception as e:
            print(f"⚠️  OAuth 認證檔案讀取失敗: {e}")
            return False


def check_config():
    """檢查設定檔案並返回認證類型"""
    config_file = Path("config/settings.yaml")
    template_file = Path("config/settings.yaml.template")

    if not config_file.exists():
        print("⚠️  設定檔案不存在")
        if template_file.exists():
            print("請複製範本檔案並填入您的資訊:")
            print("  cp config/settings.yaml.template config/settings.yaml")
        else:
            print("請建立設定檔案: config/settings.yaml")
        return None, False

    print("✓ 設定檔案存在")

    # 嘗試讀取認證類型
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        auth_type = config.get('google_calendar', {}).get('auth_type', 'oauth')
        print(f"  認證方式: {auth_type}")
        return auth_type, True

    except Exception as e:
        print(f"⚠️  設定檔案讀取失敗: {e}")
        return None, False


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
    auth_type, config_ok = check_config()

    # 根據認證類型檢查對應的認證檔案
    creds_ok = False
    if config_ok and auth_type:
        creds_ok = check_credentials(auth_type)
    elif not config_ok:
        print("\n⚠️  請先建立並設定 config/settings.yaml")
        print("    然後重新執行 setup.py 以檢查認證檔案")

    print("\n" + "=" * 40)

    if config_ok and creds_ok:
        print("✅ 安裝檢查完成！可以開始使用。")
        print("\n建議的下一步:")
        print("1. 乾跑測試: python main.py --once --dry-run")
        print("2. 執行同步: python main.py --once")
        print("3. 持續同步: python main.py")
    else:
        print("⚠️  安裝未完成，請解決上述問題後重新執行 setup.py。")

        if not config_ok:
            print("\n📝 需要建立設定檔案:")
            print("   cp config/settings.yaml.template config/settings.yaml")
            print("   然後編輯 settings.yaml 填入您的資訊")
        elif not creds_ok:
            if auth_type == "service_account":
                print("\n🔑 需要設置服務帳號認證")
                print("   詳見: docs/service_account_setup.md")
            else:
                print("\n🔑 需要設置 OAuth 認證")
                print("   詳見: docs/google_api_setup.md")


if __name__ == "__main__":
    main()