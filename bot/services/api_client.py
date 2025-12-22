import aiohttp
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(3):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200 or response.status == 201:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"Ресурс не найден: {url}")
                        return None
                    else:
                        logger.error(f"Ошибка API {response.status}: {await response.text()}")
                        if attempt == 2:  # Последняя попытка
                            return None
                        await asyncio.sleep(1 * (attempt + 1))
            except aiohttp.ClientError as e:
                logger.error(f"Ошибка подключения к API: {e}")
                if attempt == 2:
                    return None
                await asyncio.sleep(2 * (attempt + 1))

        return None

    async def get_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить задачи пользователя"""
        result = await self._request('GET', f'tasks/?telegram_user_id={user_id}')
        return result.get('results', []) if result else []

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID"""
        return await self._request('GET', f'tasks/{task_id}/')

    async def create_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создать новую задачу"""
        return await self._request('POST', 'tasks/', json=task_data)

    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить задачу"""
        return await self._request('PUT', f'tasks/{task_id}/', json=task_data)

    async def delete_task(self, task_id: str) -> bool:
        """Удалить задачу"""
        result = await self._request('DELETE', f'tasks/{task_id}/')
        return result is not None

    async def get_categories(self) -> List[Dict[str, Any]]:
        """Получить список категорий"""
        result = await self._request('GET', 'categories/')
        return result.get('results', []) if result else []

    async def toggle_task_complete(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Переключить статус выполнения задачи"""
        return await self._request('POST', f'tasks/{task_id}/toggle_complete/')

    async def get_overdue_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить просроченные задачи пользователя"""
        result = await self._request('GET', f'tasks/overdue/?telegram_user_id={user_id}')
        return result.get('results', []) if result else []