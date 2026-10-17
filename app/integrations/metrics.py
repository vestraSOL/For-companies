from typing import Protocol


class BaseMetricsRecorder(Protocol):
    """Интерфейс записи метрик"""

    def increment(self, name: str) -> None: ...


"""TODO: Добавить реализацию класса для инкремента метрик"""
