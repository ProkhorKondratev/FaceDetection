import logging
from uuid import uuid4
from pathlib import Path

import aiofiles.os as aos
import aiofiles
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)


def get_uploader() -> 'Uploader':
    return Uploader('media/images')


class Uploader:
    def __init__(self, upload_dir: str):
        self._upload_dir = upload_dir

    async def _check_upload_dir(self, upload_dir: str) -> None:
        await aos.makedirs(upload_dir, exist_ok=True)

    async def _check_image(self, image: UploadFile) -> None:
        logger.info(f'Проверка изображения {image.filename}')
        if image.content_type != 'image/jpeg':
            raise ValueError(f'Неверный формат изображения {image.content_type}')

    async def upload_image(self, image: UploadFile) -> Path:
        try:
            await self._check_upload_dir(self._upload_dir)
            await self._check_image(image)

            image_path = Path(f"{self._upload_dir}/{uuid4()}.jpeg")
            async with aiofiles.open(image_path, 'wb') as file:
                await file.write(await image.read())

            return image_path
        except Exception as e:
            logger.error(f'Ошибка при загрузке изображения: {e}')
            raise HTTPException(status_code=400, detail=str(e))
