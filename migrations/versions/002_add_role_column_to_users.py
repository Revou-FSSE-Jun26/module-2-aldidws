"""add role column to users

Revision ID: 002
Revises: 001
Create Date: 2026-08-15 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('role', sa.String(length=50), nullable=False, server_default='customer'))


def downgrade():
    op.drop_column('users', 'role')
