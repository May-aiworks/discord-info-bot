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

            # 如果不是有效網址，保留原始文字
            if not url_pattern.match(source_value):
                source_value = str(self.source.value)

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

            # 建立 Embed 訊息
            embed = discord.Embed(
                title=f"📝 {data['category']} 分享",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )

            # 分享者和 Aiworks 點在同一行（inline）
            embed.add_field(
                name="👤 分享者",
                value=interaction.user.name,
                inline=True
            )
            embed.add_field(
                name="💎 Aiworks 點",
                value=data['aiworks_points'],
                inline=True
            )

            # 主題（如果有填寫）
            if data['topic']:
                embed.add_field(
                    name="📌 主題",
                    value=data['topic'],
                    inline=False
                )

            # 總結
            embed.add_field(
                name="📄 總結",
                value=data['summary'],
                inline=False
            )

            # 來源
            embed.add_field(
                name="🔗 來源",
                value=data['source'],
                inline=False
            )

            # 補充（如果有填寫）
            if data['note']:
                embed.add_field(
                    name="📝 補充",
                    value=data['note'],
                    inline=False
                )

            # 先回應 interaction（ephemeral）告訴使用者已提交
            await interaction.response.send_message(
                '✅ 分享成功！訊息已發送到頻道。',
                ephemeral=True
            )

            # 發送公開 Embed 訊息到當前頻道
            await interaction.channel.send(embed=embed)

            # 如果有 Google Sheets，儲存資料
            if self.sheets_handler:
                self.sheets_handler.append_data(data)

        except Exception as e:
            print(f"處理表單提交時發生錯誤: {e}")
            await interaction.response.send_message(
                f'❌ 發生錯誤：{str(e)}',
                ephemeral=True
            )


class CategorySelect(Select):
    """分類選擇下拉選單"""

    def __init__(self, sheets_handler=None):
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
        """當使用者選擇分類時，直接彈出 Modal"""
        selected_category = self.values[0]
        modal = ShareModal(category=selected_category, sheets_handler=self.sheets_handler)
        await interaction.response.send_modal(modal)


class CategoryView(View):
    """包含分類選單的 View"""

    def __init__(self, sheets_handler=None):
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
        只顯示分類選擇下拉選單（極簡版）
        """
        view = CategoryView(self.sheets_handler)
        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    """
    載入 Cog 的 setup 函數
    這是 discord.py Cogs 系統的標準入口
    """
    await bot.add_cog(ShareCog(bot))
