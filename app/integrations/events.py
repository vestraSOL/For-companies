from typing import Any, Protocol


class BaseProducer(Protocol):
    """Интерфейс шины событий"""

    async def publish(self, topic: str, payload: dict[str, Any]) -> None: ...


"""TODO: Добавить реализацию продюсера для отправки Kafka событий"""
