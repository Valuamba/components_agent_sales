"""Add hash to message

Revision ID: f118c675532c
Revises: 0c39ebe955dc
Create Date: 2024-02-18 01:37:00.729252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f118c675532c'
down_revision: Union[str, None] = '0c39ebe955dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('hash', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'hash')
    # ### end Alembic commands ###
