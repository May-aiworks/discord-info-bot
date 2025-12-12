"""
Google Sheets 整合工具
處理資料寫入到 Google 試算表
"""
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import config

class SheetsHandler:
    """處理 Google Sheets 操作的類別"""

    def __init__(self):
        """初始化 Google Sheets 連接"""
        self.client = None
        self.worksheet = None
        self._authenticate()

    def _authenticate(self):
        """使用服務帳號憑證進行身份驗證"""
        try:
            # 定義存取範圍
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # 載入憑證
            credentials = Credentials.from_service_account_file(
                config.GOOGLE_CREDENTIALS_FILE,
                scopes=scopes
            )

            # 建立 gspread 客戶端
            self.client = gspread.authorize(credentials)

            # 開啟試算表
            spreadsheet = self.client.open_by_key(config.SPREADSHEET_ID)
            self.worksheet = spreadsheet.worksheet(config.WORKSHEET_NAME)

            print(f"✅ 成功連接到 Google Sheets: {config.WORKSHEET_NAME}")

        except Exception as e:
            print(f"❌ Google Sheets 連接失敗: {e}")
            raise

    def append_data(self, data):
        """
        將資料附加到試算表末端

        Args:
            data (dict): 包含以下鍵值的字典:
                - category: 分類
                - topic: 主題
                - summary: 一句話總結
                - source: 來源或連結
                - aiworks_points: Aiworks 點
                - note: 補充
                - username: 提交者用戶名
                - user_id: 提交者 Discord ID

        Returns:
            bool: 成功返回 True，失敗返回 False
        """
        try:
            # 準備要寫入的行資料
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [
                timestamp,                          # 時間戳記
                data.get('category', ''),          # 分類
                data.get('topic', ''),             # 主題
                data.get('summary', ''),           # 一句話總結
                data.get('source', ''),            # 來源或連結
                data.get('aiworks_points', ''),    # Aiworks 點
                data.get('note', ''),              # 補充
                data.get('username', ''),          # 提交者用戶名
                data.get('user_id', '')            # 提交者 ID
            ]

            # 附加到試算表
            self.worksheet.append_row(row, value_input_option='USER_ENTERED')
            print(f"✅ 資料已寫入 Google Sheets: {data.get('summary', '')}")
            return True

        except Exception as e:
            print(f"❌ 寫入 Google Sheets 失敗: {e}")
            return False

    def initialize_headers(self):
        """初始化試算表標題行（僅在首次使用時需要）"""
        try:
            # 檢查第一行是否已有資料
            first_row = self.worksheet.row_values(1)

            if not first_row or first_row[0] == '':
                headers = [
                    '時間戳記',
                    '分類',
                    '主題',
                    '一句話總結',
                    '來源或連結',
                    'Aiworks 點',
                    '補充',
                    '提交者',
                    '提交者 ID'
                ]
                self.worksheet.insert_row(headers, 1)
                print("✅ 已初始化試算表標題")
            else:
                print("ℹ️ 試算表標題已存在")

        except Exception as e:
            print(f"❌ 初始化標題失敗: {e}")
