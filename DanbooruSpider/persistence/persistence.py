import json
from pathlib import Path
from shutil import move as moveFile
from typing import Any, Dict

from ..config import Config
from ..log import logger
from ..spider.models import ImageDownload
from ..utils import AsyncOpen, SyncToAsync

IMAGE_PATH = Path(".") / "data" / "images"
HASH_DEPTH: int = Config["persistence"]["path-depth"].as_number()

IMAGE_PATH.mkdir(parents=True, exist_ok=True)


class Persistence:
    @staticmethod
    def verify(image: ImageDownload) -> bool:
        assert image.md5
        return image.data.imageMD5.lower() == image.md5.lower()

    @staticmethod
    @SyncToAsync
    def _dump(data: Dict[str, Any]) -> str:
        return json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)

    @staticmethod
    @SyncToAsync
    def _move(source: Path, destination: Path) -> None:
        moveFile(str(source), str(destination))

    @classmethod
    async def save(cls, image: ImageDownload) -> Path:
        folder = IMAGE_PATH / ("/".join(image.md5[:HASH_DEPTH]))
        folder.mkdir(parents=True, exist_ok=True)
        filePath = folder / f"{image.md5}.{image.data.imageExt}"
        metadataPath = folder / f"{image.md5}.json"
        await cls._move(image.path, filePath)
        async with AsyncOpen(metadataPath, "wt", encoding="utf-8") as f:
            await f.write(await cls._dump(image.data.dict()))
        logger.trace(
            f"Picture {image.data.id} has been successfully saved to path {filePath}"
        )
        return filePath
