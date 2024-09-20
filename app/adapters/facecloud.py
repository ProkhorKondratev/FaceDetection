from typing import AsyncGenerator
from pathlib import Path

from fastapi import Depends, HTTPException
import httpx
import aiofiles

from app.settings import settings


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client


async def get_facecloud(client: httpx.AsyncClient = Depends(get_http_client)) -> 'FaceCloud':
    return FaceCloud(
        client,
        settings.FACECLOUD_API_URL,
        settings.FACECLOUD_API_EMAIL,
        settings.FACECLOUD_API_PASSWORD,
    )


class FaceCloud:
    def __init__(self, client: httpx.AsyncClient, api_url: str, email: str, password: str):
        self._client = client
        self._api_url = api_url
        self._api_email = email
        self._api_password = password
        self._api_token = None

    async def _authenticate(self) -> None:
        """Получает и сохраняет токен аутентификации."""
        try:
            response = await self._client.post(
                f'{self._api_url}/login',
                json={'email': self._api_email, 'password': self._api_password},
            )
            response.raise_for_status()
            self._api_token = response.json()['data']['access_token']
        except httpx.HTTPStatusError:
            raise HTTPException(401, 'Ошибка аутентификации в FaceCloud')

    async def get_token(self) -> str:
        """Возвращает токен аутентификации, если он еще не получен — запрашивает новый."""
        if not self._api_token:
            await self._authenticate()
        return self._api_token

    async def detect_faces(self, image_path: Path) -> dict:
        """Отправляет изображение для обнаружения лиц и возвращает результат."""
        token = await self.get_token()

        async with aiofiles.open(image_path, 'rb') as image_file:
            try:
                image_data = await image_file.read()
                response = await self._client.post(
                    f"{self._api_url}/detect",
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'image/jpeg',
                    },
                    content=image_data,
                    params={
                        'demographics': 'true',
                    },
                )
                response.raise_for_status()
                return response.json()['data']
            except httpx.HTTPStatusError:
                raise HTTPException(400, 'Ошибка обработки изображения в FaceCloud')
