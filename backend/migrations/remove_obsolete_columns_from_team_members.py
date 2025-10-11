"""Remove obsolete columns from team_members table.

Revision ID: 202410032240
Revises: 
Create Date: 2024-10-03 22:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '202410032240'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Supprimer les colonnes obsolètes
    with op.batch_alter_table('team_members', schema=None) as batch_op:
        batch_op.drop_column('is_admin')
        batch_op.drop_column('joined_at')
        batch_op.drop_column('left_at')
        batch_op.drop_column('is_active')


def downgrade() -> None:
    # Recréer les colonnes (pour rollback)
    with op.batch_alter_table('team_members', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.BOOLEAN(), nullable=False, server_default=sa.text('1')))
        batch_op.add_column(sa.Column('left_at', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('joined_at', sa.DATETIME(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
        batch_op.add_column(sa.Column('is_admin', sa.BOOLEAN(), nullable=False, server_default=sa.text('0')))
