"""Add modules relationship with project

Revision ID: 4fe52bfbfee9
Revises: 178e0eb26f31
Create Date: 2024-12-03 03:18:19.348750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fe52bfbfee9'
down_revision: Union[str, None] = '178e0eb26f31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
