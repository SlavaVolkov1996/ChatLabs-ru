import aiohttp
from config import API_URL


class APIClient:
    """Клиент для работы с Django REST API"""

    def __init__(self):
        self.base_url = API_URL

    async def get_tasks(self, user_id: int):
        """Получить задачи пользователя"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/tasks/?user_id={user_id}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Ошибка API: {response.status}")
                        return []
        except Exception as e:
            print(f"Ошибка подключения к API: {e}")
            return []

    async def create_task(self, task_data: dict):
        """Создать новую задачу"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/tasks/"
                async with session.post(url, json=task_data) as response:
                    return response.status == 201
        except Exception as e:
            print(f"Ошибка создания задачи: {e}")
            return False

    async def get_categories(self):
        """Получить список категорий"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/categories/"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    return []
        except Exception as e:
            print(f"Ошибка получения категорий: {e}")
            return []