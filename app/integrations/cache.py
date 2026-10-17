from typing import Protocol


class BaseCacheBackend(Protocol):
    """Интерфейс кеша"""

    async def get(self, key: str) -> str | None: ...
    async def set(
        self, key: str, value: str, ttl_seconds: int | None = None
    ) -> None: ...
    async def delete(self, key: str) -> None: ...


"""TODO: Добавить реализацию класса для работы с кешем Redis"""
