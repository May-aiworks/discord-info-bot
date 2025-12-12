"""
Help Cog - 顯示機器人所有可用功能
提供 /help 斜線指令來查看所有功能列表
"""
import discord
from discord import app_commands
from discord.ext import commands


class HelpCog(commands.Cog):
    """幫助指令 Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="顯示機器人所有可用功能")
    async def help(self, interaction: discord.Interaction):
        """
        /help 指令
        顯示所有可用的斜線指令和說明
        """
        # 建立 Embed 訊息
        embed = discord.Embed(
            title="📚 機器人功能列表",
            description="以下是目前可用的所有指令：",
            color=discord.Color.blue()
        )

        # 取得所有已註冊的斜線指令
        commands_list = self.bot.tree.get_commands()

        if commands_list:
            for cmd in commands_list:
                # 取得指令名稱和說明
                cmd_name = cmd.name
                cmd_description = cmd.description or "無說明"

                # 加入到 Embed
                embed.add_field(
                    name=f"/{cmd_name}",
                    value=cmd_description,
                    inline=False
                )
        else:
            embed.add_field(
                name="⚠️ 沒有可用指令",
                value="目前沒有註冊任何斜線指令",
                inline=False
            )

        # 加入 Cogs 資訊（選用）
        cogs_info = []
        for cog_name, cog in self.bot.cogs.items():
            cogs_info.append(f"`{cog_name}`")

        if cogs_info:
            embed.add_field(
                name="🔧 已載入的功能模組",
                value=" • ".join(cogs_info),
                inline=False
            )

        # 加入頁尾
        embed.set_footer(text="💡 提示：所有指令都是斜線指令，輸入 / 即可查看")

        # 發送 ephemeral 訊息（只有使用者看得到）
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """
    載入 Cog 的 setup 函數
    """
    await bot.add_cog(HelpCog(bot))
