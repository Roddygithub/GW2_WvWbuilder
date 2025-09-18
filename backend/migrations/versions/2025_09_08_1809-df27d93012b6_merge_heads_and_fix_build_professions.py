"""merge heads and fix build_professions

Revision ID: df27d93012b6
Revises: drop_and_recreate_build_professions, fix_build_professions_table
Create Date: 2025-09-08 18:09:21.930407+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df27d93012b6'
down_revision: Union[str, Sequence[str], None] = ('drop_and_recreate_build_professions', 'fix_build_professions_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
