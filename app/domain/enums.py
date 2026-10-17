from enum import IntEnum, StrEnum


class FieldDataType(IntEnum):
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    TEXT = 3
    BOOL = 4
    SWITCH = 5
    ARRAY = 6
    DATA = 7
    DATA_ARRAY = 8
    PHONE = 9
    LINK = 10
    EMAIL = 11
    TIME = 12
    DATETIME = 13
    PEOPLE = 14


class TaskStatus(IntEnum):
    UNKNOWN = 0
    NEW = 1
    IN_PROGRESS = 2
    ON_HOLD = 3
    NEED_REVIEW = 4
    DONE = 5
    CANCELED = 6


TASK_STATUS_LABELS: dict[int, str] = {
    TaskStatus.UNKNOWN: "Необработана",
    TaskStatus.NEW: "Новая",
    TaskStatus.IN_PROGRESS: "В работе",
    TaskStatus.ON_HOLD: "Приостановлена",
    TaskStatus.NEED_REVIEW: "На проверке",
    TaskStatus.DONE: "Завершена",
    TaskStatus.CANCELED: "Отменена",
}


class CatalogName(StrEnum):
    USERS = "users"
    COMPANIES = "companies"
    GOODS = "goods"


RESERVED_CATALOG_NAMES = {item.value for item in CatalogName}
