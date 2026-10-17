from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import Select


def active(query: Select, model: Any) -> Select:
    """Добавляет фильтр по мягкому удалению"""

    return query.where(model.deleted_at.is_(None))


def as_string_list(values: Sequence[UUID | str | None]) -> list[str]:
    """Преобразует значения в список строк"""

    normalized: list[str] = []
    for value in values:
        if value is None:
            continue
        as_string = str(value)
        if as_string not in normalized:
            normalized.append(as_string)
    return normalized
