"""add outbox table

Revision ID: 80e4497511aa
Revises: 14f4f8a63f12
Create Date: 2025-12-19 21:45:39.289767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80e4497511aa'
down_revision: Union[str, Sequence[str], None] = '14f4f8a63f12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['event_id'], ['events_finder.event.id'], ),
        schema='events_finder'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('notifications', schema='events_finder')
