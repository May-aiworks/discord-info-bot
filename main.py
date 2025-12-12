"""
Discord 資訊分享機器人 - 主程式
使用 Cogs 架構組織程式碼
"""
import asyncio
import discord
from discord.ext import commands
import config

# 初始化 Bot（使用 commands.Bot 而非 discord.Client）
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',  # 雖然我們主要使用斜線指令，但 commands.Bot 需要 prefix
    intents=intents,
    help_command=None  # 停用預設的 help 指令
)


@bot.event
async def on_ready():
    """當機器人準備就緒時執行"""
    print(f'✅ {bot.user} 已成功登入！')
    print(f'機器人 ID: {bot.user.id}')
    print('---')

    # 載入所有 Cogs
    await load_cogs()

    # 同步斜線指令到 Discord
    try:
        synced = await bot.tree.sync()
        print(f'✅ 已同步 {len(synced)} 個斜線指令')
    except Exception as e:
        print(f'❌ 同步指令失敗: {e}')

    print('🚀 機器人已準備就緒！')


async def load_cogs():
    """載入所有 Cogs"""
    cogs_to_load = [
        'cogs.share',  # 分享功能 Cog
        'cogs.help',   # 幫助功能 Cog
    ]

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f'✅ 已載入 Cog: {cog}')
        except Exception as e:
            print(f'❌ 載入 Cog 失敗 ({cog}): {e}')


@bot.command(name='reload')
@commands.is_owner()
async def reload_cog(ctx, cog_name: str):
    """重新載入指定的 Cog（僅限 Bot 擁有者）"""
    try:
        await bot.reload_extension(f'cogs.{cog_name}')
        await ctx.send(f'✅ 已重新載入 Cog: {cog_name}')
        # 重新同步指令
        await bot.tree.sync()
    except Exception as e:
        await ctx.send(f'❌ 重新載入失敗: {e}')


def main():
    """主程式入口"""
    # 驗證配置
    try:
        config.validate_config()
    except ValueError as e:
        print(f'❌ 配置錯誤: {e}')
        return

    # 啟動機器人
    try:
        bot.run(config.DISCORD_TOKEN)
    except Exception as e:
        print(f'❌ 機器人啟動失敗: {e}')


if __name__ == '__main__':
    main()
