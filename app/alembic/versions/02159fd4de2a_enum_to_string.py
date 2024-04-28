"""Enum to string

Revision ID: 02159fd4de2a
Revises: 53e6c080b076
Create Date: 2024-04-27 01:14:30.290412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '02159fd4de2a'
down_revision: Union[str, None] = '53e6c080b076'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('agent_task', 'status',
               existing_type=postgresql.ENUM('Failed', 'Passed', 'Stopped', name='statustype'),
               type_=sa.String(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('agent_task', 'status',
               existing_type=sa.String(),
               type_=postgresql.ENUM('Failed', 'Passed', 'Stopped', name='statustype'),
               existing_nullable=False)
    # ### end Alembic commands ###
