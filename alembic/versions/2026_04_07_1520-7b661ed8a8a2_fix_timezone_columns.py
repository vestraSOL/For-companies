"""fix timezone-aware business datetime columns

Revision ID: 7b661ed8a8a2
Revises: e01195725eac
Create Date: 2026-04-07 15:20:00

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b661ed8a8a2"
down_revision: Union[str, Sequence[str], None] = "e01195725eac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "valid_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="valid_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "users",
        "validation_sent_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="validation_sent_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "activity_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="activity_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "finish_to",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="finish_to AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "finished_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="finished_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "reminders",
        "date_from",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="date_from AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "reminders",
        "date_to",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="date_to AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    op.alter_column(
        "reminders",
        "date_to",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="date_to AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "reminders",
        "date_from",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="date_from AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "finished_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="finished_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "finish_to",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="finish_to AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "tasks",
        "activity_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="activity_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "users",
        "validation_sent_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="validation_sent_at AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "users",
        "valid_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="valid_at AT TIME ZONE 'UTC'",
    )
