"""Optimize database indexes and constraints

Revision ID: 123456789abc
Revises: <previous_migration_id>
Create Date: 2025-10-08 21:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Identifiants de révision
revision = '123456789abc'
down_revision = '<previous_migration_id>'
branch_labels = None
depends_on = None

def upgrade():
    # Récupère le nom du moteur de base de données
    bind = op.get_bind()
    is_postgres = bind.engine.name == 'postgresql'
    is_sqlite = bind.engine.name == 'sqlite'
    
    # Désactiver temporairement les contraintes de clé étrangère
    if is_sqlite:
        op.execute('PRAGMA foreign_keys=OFF')
    
    # Optimisation des index pour la table builds
    op.create_index('idx_builds_created_public', 'builds', 
                   ['created_by_id', 'is_public', 'game_mode'], 
                   postgresql_where=sa.text('is_public = true'),
                   unique=False)
    
    # Optimisation des index pour la table teams
    op.create_index('idx_teams_owner_public', 'teams', 
                   ['owner_id', 'is_public'], 
                   postgresql_where=sa.text('is_public = true'),
                   unique=False)
    
    # Optimisation des index pour la table team_members
    op.create_index('idx_team_members_team_user', 'team_members', 
                   ['team_id', 'user_id', 'is_active'], 
                   unique=False)
    
    # Ajout de contraintes manquantes
    op.create_foreign_key(
        'fk_teams_owner_id_users',
        'teams', 'users',
        ['owner_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Réactiver les contraintes de clé étrangère
    if is_sqlite:
        op.execute('PRAGMA foreign_keys=ON')
    
    # Pour PostgreSQL, on peut ajouter des optimisations spécifiques
    if is_postgres:
        op.execute('VACUUM ANALYZE')


def downgrade():
    # Suppression des index créés
    op.drop_index('idx_builds_created_public', 'builds')
    op.drop_index('idx_teams_owner_public', 'teams')
    op.drop_index('idx_team_members_team_user', 'team_members')
    
    # On ne supprime pas la contrainte de clé étrangère car elle devrait exister déjà
