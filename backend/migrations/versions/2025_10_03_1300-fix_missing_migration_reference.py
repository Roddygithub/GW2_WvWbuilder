"""fix_missing_migration_reference

Revision ID: a1b2c3d4e5f6
Revises: df27d93012b6
Create Date: 2025-10-03 13:00:00.000000+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "df27d93012b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Vérifier si la table build_professions existe
    conn = op.get_bind()
    inspector = sa.inspect(conn.engine)
    
    if 'build_professions' not in inspector.get_table_names():
        # Créer la table manquante si elle n'existe pas
        op.create_table(
            'build_professions',
            sa.Column('build_id', sa.Integer(), nullable=False),
            sa.Column('profession_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['build_id'], ['builds.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['profession_id'], ['professions.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('build_id', 'profession_id')
        )
        
        # Ajouter un index pour améliorer les performances des requêtes
        op.create_index(
            'ix_build_professions_build_id', 
            'build_professions', 
            ['build_id']
        )
        op.create_index(
            'ix_build_professions_profession_id', 
            'build_professions', 
            ['profession_id']
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Ne pas supprimer la table en cas de rollback pour éviter de perdre des données
    # Cette migration est destinée à corriger un problème de référence manquante
    pass
