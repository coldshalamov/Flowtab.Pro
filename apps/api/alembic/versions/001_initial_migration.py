"""Initial migration for the prompts table

Revision ID: 001
Revises: 
Create Date: 2026-01-17 05:18:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Create the prompts table
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if not inspector.has_table('prompts'):
        op.create_table(
            'prompts',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('slug', sa.String(255), nullable=False),
            sa.Column('title', sa.String(500), nullable=False),
            sa.Column('summary', sa.Text(), nullable=False),
            sa.Column('difficulty', sa.String(20), nullable=False),
            sa.Column('worksWith', postgresql.JSON(astext_type=sa.Text()), nullable=False),
            sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=False),
            sa.Column('targetSites', postgresql.JSON(astext_type=sa.Text()), nullable=False),
            sa.Column('promptText', sa.Text(), nullable=False),
            sa.Column('steps', postgresql.JSON(astext_type=sa.Text()), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        )
        
        # Create unique constraint on slug
        op.create_unique_constraint('uq_prompts_slug', 'prompts', ['slug'])
        
        # Create indexes
        op.create_index('ix_prompts_slug', 'prompts', ['slug'], unique=False)
        op.create_index('idx_difficulty', 'prompts', ['difficulty'], unique=False)
        op.create_index('idx_created_at', 'prompts', ['createdAt'], unique=False)
        op.create_index('idx_updated_at', 'prompts', ['updatedAt'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if inspector.has_table('prompts'):
        # Drop indexes
        op.drop_index('idx_updated_at', table_name='prompts')
        op.drop_index('idx_created_at', table_name='prompts')
        op.drop_index('idx_difficulty', table_name='prompts')
        op.drop_index('ix_prompts_slug', table_name='prompts')
        
        # Drop unique constraint on slug
        op.drop_constraint('uq_prompts_slug', 'prompts', type_='unique')
        
        # Drop the prompts table
        op.drop_table('prompts')
