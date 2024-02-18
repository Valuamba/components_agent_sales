"""Add hash to message

Revision ID: 21cc57fa8bcd
Revises: ea5f01170678
Create Date: 2024-02-18 01:32:35.533373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21cc57fa8bcd'
down_revision: Union[str, None] = 'ea5f01170678'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
