import asyncio
from jmcomic import *
from pathlib import Path

def setup_jmconfig(config: dict):
    """配置JMComic参数"""
    jm_debug(False)
    set_jm_global_domain(config.get("proxy"))
    set_download_cache(True)

async def async_download(album_id: int, save_dir: str):
    """异步下载入口"""
    loop = asyncio.get_event_loop()
    save_path = Path(save_dir) / str(album_id)
    
    return await loop.run_in_executor(
        None,
        lambda: download_album(
            str(album_id),
            option=create_option(
                f"--save-dir={save_path} "
                f"--image-suffix=.webp "
                f"--download-archive"
            )
        )
    )