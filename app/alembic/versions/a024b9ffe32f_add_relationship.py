"""Add relationship

Revision ID: a024b9ffe32f
Revises: 3703b19163f4
Create Date: 2024-04-25 23:14:32.918542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a024b9ffe32f'
down_revision: Union[str, None] = '3703b19163f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'taskfeedback_issue_link', 'issue', ['issue_id'], ['issue_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'taskfeedback_issue_link', type_='foreignkey')
    # ### end Alembic commands ###
