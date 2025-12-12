"""
Share Cog - 處理資訊分享功能
包含 /share 指令、分類選單、Modal 表單等
"""
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View
import re
import config
# from utils.sheets import SheetsHandler  # 暫時停用 Google Sheets


class ShareModal(discord.ui.Modal, title='分享資訊'):
    """資訊分享的 Modal 表單"""

    def __init__(self, category: str, sheets_handler=None):  # sheets_handler 暫時停用
        super().__init__()
        self.category = category
        self.sheets_handler = sheets_handler

    # 主題（選填）
    topic = discord.ui.TextInput(
        label='主題',
        placeholder='請輸入主題（選填）',
        required=False,
        max_length=100
    )

    # 一句話總結（必填）
    summary = discord.ui.TextInput(
        label='一句話總結',
        placeholder='請用一句話總結這則資訊',
        required=True,
        max_length=200
    )

    # 來源或連結（必填）
    source = discord.ui.TextInput(
        label='來源或連結',
        placeholder='請輸入網址或其他來源資訊',
        required=True,
        max_length=500
    )

    # Aiworks 點（必填）
    aiworks_points = discord.ui.TextInput(
        label='Aiworks 點',
        placeholder='請輸入 Aiworks 點數（可填「無」）',
        required=True,
        max_length=50
    )

    # 補充（選填）
    note = discord.ui.TextInput(
        label='補充',
        placeholder='其他補充說明（選填）',
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        """當使用者提交表單時的處理"""
        try:
            # 驗證來源是否為網址，如果不是則使用訊息連結
            source_value = str(self.source.value)
            url_pattern = re.compile(
                r'^https?://'  # http:// 或 https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
                r'(?::\d+)?'  # 可選端口
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

            # 如果不是有效網址，嘗試取得當前訊息連結
            if not url_pattern.match(source_value):
                if interaction.message:
                    # 建立訊息連結
                    guild_id = interaction.guild_id
                    channel_id = interaction.channel_id
                    message_id = interaction.message.id
                    source_value = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
                    source_value += f"\n原始內容：{self.source.value}"

            # 準備要儲存的資料
            data = {
                'category': self.category,
                'topic': str(self.topic.value) if self.topic.value else '',
                'summary': str(self.summary.value),
                'source': source_value,
                'aiworks_points': str(self.aiworks_points.value),
                'note': str(self.note.value) if self.note.value else '',
                'username': interaction.user.name,
                'user_id': str(interaction.user.id)
            }

            # 儲存到 Google Sheets（暫時停用）
            if self.sheets_handler:
                success = self.sheets_handler.append_data(data)
                if success:
                    await interaction.response.send_message(
                        '✅ 儲存成功！感謝你的分享！',
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        '❌ 儲存失敗，請稍後再試或聯絡管理員。',
                        ephemeral=True
                    )
            else:
                # Google Sheets 停用時，只顯示接收到的資料
                summary_text = (
                    f"✅ 已接收你的分享！\n\n"
                    f"**分類**：{data['category']}\n"
                    f"**主題**：{data['topic'] or '（未填寫）'}\n"
                    f"**總結**：{data['summary']}\n"
                    f"**來源**：{data['source']}\n"
                    f"**Aiworks 點**：{data['aiworks_points']}\n"
                    f"**補充**：{data['note'] or '（未填寫）'}\n\n"
                    f"ℹ️ Google Sheets 功能目前停用，資料未儲存"
                )
                await interaction.response.send_message(
                    summary_text,
                    ephemeral=True
                )

        except Exception as e:
            print(f"處理表單提交時發生錯誤: {e}")
            await interaction.response.send_message(
                f'❌ 發生錯誤：{str(e)}',
                ephemeral=True
            )


class CategorySelect(Select):
    """分類選擇下拉選單"""

    def __init__(self, sheets_handler=None):  # sheets_handler 暫時停用
        self.sheets_handler = sheets_handler

        # 建立選項
        options = [
            discord.SelectOption(label=category, value=category)
            for category in config.CATEGORIES
        ]

        super().__init__(
            placeholder='請選擇分類...',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        """當使用者選擇分類時的回調"""
        selected_category = self.values[0]

        # 顯示 Modal 表單
        modal = ShareModal(category=selected_category, sheets_handler=self.sheets_handler)
        await interaction.response.send_modal(modal)


class CategoryView(View):
    """包含分類選單的 View"""

    def __init__(self, sheets_handler=None):  # sheets_handler 暫時停用
        super().__init__(timeout=180)  # 3 分鐘後超時
        self.add_item(CategorySelect(sheets_handler))

class ShareCog(commands.Cog):
    """分享功能 Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sheets_handler = None

    async def cog_load(self):
        """Cog 載入時執行(初始化 Google Sheets)"""
        # 暫時註解掉 Google Sheets 功能
        # try:
        #     self.sheets_handler = SheetsHandler()
        #     # 如果是第一次使用，初始化標題行
        #     self.sheets_handler.initialize_headers()
        #     print('✅ Google Sheets 已連接')
        # except Exception as e:
        #     print(f'❌ Google Sheets 初始化失敗: {e}')
        #     print('⚠️ 分享功能將無法正常運作')
        print('ℹ️ Google Sheets 功能已暫時停用')

    @app_commands.command(name="infoshare", description="分享有用的資訊、文章或資源")
    async def share(self, interaction: discord.Interaction):
        """
        /infoshare 指令
        顯示分類選擇下拉選單
        """
        # 暫時註解掉 Google Sheets 檢查（但保留 UI 功能）
        # if not self.sheets_handler:
        #     await interaction.response.send_message(
        #         '❌ Google Sheets 尚未初始化，請聯絡管理員。',
        #         ephemeral=True
        #     )
        #     return

        view = CategoryView(self.sheets_handler)
        await interaction.response.send_message(
            '📝 請選擇要分享的資訊類別：',
            view=view,
            ephemeral=True  # 只有使用者自己看得到
        )

async def setup(bot: commands.Bot):
    """
    載入 Cog 的 setup 函數
    這是 discord.py Cogs 系統的標準入口
    """
    await bot.add_cog(ShareCog(bot))
