"""add_schema

Revision ID: 5221143c1665
Revises: 
Create Date: 2025-12-10 21:23:48.271528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5221143c1665'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("create schema events_finder")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop schema events_finder")
    pass
