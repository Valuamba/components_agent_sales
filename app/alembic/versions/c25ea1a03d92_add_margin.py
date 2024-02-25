"""Add margin

Revision ID: c25ea1a03d92
Revises: 61e50252005c
Create Date: 2024-02-23 01:26:09.066262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c25ea1a03d92'
down_revision: Union[str, None] = '61e50252005c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('purchase_history', sa.Column('deal_id', sa.Integer(), nullable=False))
    op.add_column('purchase_history', sa.Column('margin', sa.Float(), nullable=True))
    op.drop_column('purchase_history', 'id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('purchase_history', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_column('purchase_history', 'margin')
    op.drop_column('purchase_history', 'deal_id')
    # ### end Alembic commands ###
