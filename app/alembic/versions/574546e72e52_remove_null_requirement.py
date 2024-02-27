"""Remove Null requirement

Revision ID: 574546e72e52
Revises: 1b58112b8d3d
Create Date: 2024-02-17 02:13:29.691782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '574546e72e52'
down_revision: Union[str, None] = '1b58112b8d3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('agent_task', 'completion_cost',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('agent_task', 'output_tokens',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('agent_task', 'prompt_tokens',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('agent_task', 'response',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('deal', 'customer',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('message', 'sent_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('part_inquiry', 'full_brand_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('task_feedback', 'feedback',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('task_feedback', 'feedback',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('part_inquiry', 'full_brand_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('message', 'sent_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('deal', 'customer',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('agent_task', 'response',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('agent_task', 'prompt_tokens',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('agent_task', 'output_tokens',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('agent_task', 'completion_cost',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
    # ### end Alembic commands ###