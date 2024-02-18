"""Add hash to message

Revision ID: 0c39ebe955dc
Revises: 21cc57fa8bcd
Create Date: 2024-02-18 01:35:33.521935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c39ebe955dc'
down_revision: Union[str, None] = '21cc57fa8bcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
