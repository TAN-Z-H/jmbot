from nonebot import on_command, get_driver
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import (
    Event,
    Message,
    MessageEvent,
    MessageSegment
)
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from .jm_downloader import async_download
from .config import Config
import re

config = Config.load()
bot_id = get_driver().config.self_id

# region 自定义规则
async def is_at_bot(event: Event) -> bool:
    """验证是否@机器人"""
    if not isinstance(event, MessageEvent):
        return False
    # 私聊直接通过
    if event.get_session_id().startswith("private"):
        return True
    
    # 群聊需要@机器人
    msg = event.get_message()
    return any(
        seg.type == "at" and str(seg.data.get("qq", "")) == str(bot_id)
        for seg in msg
    )

jm_rule = Rule(is_at_bot)
# endregion

# region 命令处理器
jm = on_command(
    "jm",
    aliases={"JM漫画"},
    rule=jm_rule,
    priority=5,
    block=True
)

@jm.handle()
async def handle_jm_command(
    event: MessageEvent,
    args: Message = CommandArg()
):
    # 权限验证
    if not await validate_permission(event):
        await jm.finish("❌ 权限不足或未正确@机器人")
    
    # 提取命令参数
    album_id = await parse_command(event, args)
    if not album_id:
        await jm.finish("❌ 格式错误，正确格式：@机器人 jm <漫画ID>")
    
    # 确认流程
    await start_download(event, album_id)

async def validate_permission(event: MessageEvent) -> bool:
    """复合权限验证"""
    session_id = event.get_session_id()
    
    # 私聊直接允许
    if session_id.startswith("private"):
        return True
    
    # 超级用户允许
    if await SUPERUSER(bot, event):
        return True
    
    # 群组白名单验证
    group_id = getattr(event, "group_id", None)
    return group_id and (group_id in config.allow_groups)

async def parse_command(event: MessageEvent, args: Message) -> str:
    """解析命令参数"""
    raw_msg = event.get_plaintext().strip()
    
    # 清理@机器人标记
    clean_msg = re.sub(r"@\S+\s+", "", raw_msg, count=1)
    cmd_parts = clean_msg.split(maxsplit=1)
    
    return cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

async def start_download(event: MessageEvent, album_id: str):
    """下载流程控制"""
    if not album_id.isdigit():
        await jm.finish("❌ 请输入有效的漫画ID数字")
    
    # 确认提示
    await jm.send(f"⚠️ 确认下载漫画 #{album_id}？(回复 Y 确认)")
    
    # 等待用户确认
    @jm.receive()
    async def confirm_download(confirm_event: MessageEvent):
        if confirm_event.get_plaintext().strip().lower() != "y":
            await jm.finish("操作已取消")
        
        try:
            await jm.send(f"🔄 开始下载漫画 #{album_id}...")
            await async_download(int(album_id), config.save_path)
            
            await jm.finish(
                MessageSegment.text("✅ 下载完成！路径：") +
                MessageSegment.image(f"file:///{config.save_path}/{album_id}/cover.jpg")
            )
        except Exception as e:
            await jm.finish(f"⚠️ 下载失败：{str(e)}")
# endregion