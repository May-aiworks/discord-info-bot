# Discord 資訊分享機器人

使用 **Cogs 架構**建立的 Discord 機器人。

## 專案架構

```
discord-info-bot/
├── main.py                 # 主程式（使用 commands.Bot）
├── config.py               # 配置檔案
├── .env                    # 環境變數設定
├── .gitignore             # Git 忽略清單
├── requirements.txt        # Python 套件清單
├── credentials.json        # Google API 憑證（不要上傳到 Git）
├── cogs/                   # Cogs 模組（功能模組）
│   ├── __init__.py
│   ├── share.py           # 分享功能 Cog
│   └── help.py            # 幫助功能 Cog
├── utils/                  # 工具模組
│   ├── __init__.py
│   └── sheets.py          # Google Sheets 整合
└── myenv/                  # Python 虛擬環境
```

## 可用指令

- `/help` - 顯示所有可用功能
- `/InfoShare` - 分享資訊到 Google Sheets

## UX 流程

### `/InfoShare` 指令流程

1. 使用者輸入指令：`/InfoShare`
2. Bot 回覆 ephemeral 訊息（只有使用者看得到）
    1. 顯示：請選擇標籤（下拉選單）
    2. 使用者選擇分類
    3. 彈出 Modal（表單）
        - 主題（選填）
        - 一句話總結（必填）
        - 來源或連結（必填）→ 如果解析出來非網址就變成儲存該條訊息的連結
        - Aiworks 點（必填）→ 可以填「無」
        - 補充（選填）
3. 使用者送出表單
4. 後台記錄資料
5. 資料進入 Google Sheets
6. Bot 回覆：「儲存成功！」（ephemeral）
