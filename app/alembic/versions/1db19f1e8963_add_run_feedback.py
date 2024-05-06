"""Add run feedback

Revision ID: 1db19f1e8963
Revises: 685a8e5ea59e
Create Date: 2024-05-06 10:06:19.741828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1db19f1e8963'
down_revision: Union[str, None] = '685a8e5ea59e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task_feedback', sa.Column('run_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'task_feedback', 'runs', ['run_id'], ['run_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task_feedback', type_='foreignkey')
    op.drop_column('task_feedback', 'run_id')

    # ### end Alembic commands ###