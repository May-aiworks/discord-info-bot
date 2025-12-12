"""
配置文件 - 載入環境變數和常數設定
"""
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# Discord 設定
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Google Sheets 設定
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
WORKSHEET_NAME = os.getenv('WORKSHEET_NAME', 'Sheet1')

# 分類選項
CATEGORIES = [
    "技術文章",
    "工具推薦",
    "學習資源",
    "專案分享",
    "其他"
]

# 驗證必要設定
def validate_config():
    """驗證必要的環境變數是否已設定"""
    if not DISCORD_TOKEN:
        raise ValueError("請在 .env 檔案中設定 DISCORD_TOKEN")
    if not SPREADSHEET_ID:
        raise ValueError("請在 .env 檔案中設定 SPREADSHEET_ID")
    return True
