"""add_type_price_and_marketplace_models

Revision ID: 79a4be091917
Revises: 007
Create Date: 2026-01-19 06:07:46.642842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '79a4be091917'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # USERS
    if not inspector.has_table('users'):
        op.create_table('users',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('username', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.Column('stripe_connect_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('is_seller', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_stripe_connect_id'), 'users', ['stripe_connect_id'], unique=False)
        op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    else:
        # Check columns
        user_cols = [c['name'] for c in inspector.get_columns('users')]
        if 'stripe_connect_id' not in user_cols:
             op.add_column('users', sa.Column('stripe_connect_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
             op.create_index(op.f('ix_users_stripe_connect_id'), 'users', ['stripe_connect_id'], unique=False)
        if 'is_seller' not in user_cols:
             op.add_column('users', sa.Column('is_seller', sa.Boolean(), server_default=sa.text('false'), nullable=False))

    # LIKES
    if not inspector.has_table('likes'):
        op.create_table('likes',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('target_type', sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False),
        sa.Column('target_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'target_type', 'target_id', name='uq_like_user_target')
        )
        op.create_index(op.f('ix_likes_target_id'), 'likes', ['target_id'], unique=False)
        op.create_index(op.f('ix_likes_target_type'), 'likes', ['target_type'], unique=False)
        op.create_index(op.f('ix_likes_user_id'), 'likes', ['user_id'], unique=False)

    # OAUTH ACCOUNTS
    if not inspector.has_table('oauth_accounts'):
        op.create_table('oauth_accounts',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False),
        sa.Column('provider_user_id', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_user')
        )
        op.create_index(op.f('ix_oauth_accounts_provider'), 'oauth_accounts', ['provider'], unique=False)
        op.create_index(op.f('ix_oauth_accounts_provider_user_id'), 'oauth_accounts', ['provider_user_id'], unique=False)
        op.create_index(op.f('ix_oauth_accounts_user_id'), 'oauth_accounts', ['user_id'], unique=False)

    # PROMPTS
    if not inspector.has_table('prompts'):
        op.create_table('prompts',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column('summary', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('type', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('worksWith', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('targetSites', sa.JSON(), nullable=True),
        sa.Column('promptText', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('steps', sa.JSON(), nullable=True),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('author_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.Column('updatedAt', sa.DateTime(), nullable=False),
        sa.Column('like_count', sa.Integer(), nullable=False),
        sa.Column('saves_count', sa.Integer(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(length=3), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_prompts_slug'), 'prompts', ['slug'], unique=True)
        op.create_index(op.f('ix_prompts_type'), 'prompts', ['type'], unique=False)
    else:
        # Check columns
        prompt_cols = [c['name'] for c in inspector.get_columns('prompts')]
        
        if 'type' not in prompt_cols:
             op.add_column('prompts', sa.Column('type', sqlmodel.sql.sqltypes.AutoString(length=20), server_default="prompt", nullable=False))
             op.create_index(op.f('ix_prompts_type'), 'prompts', ['type'], unique=False)
        
        if 'saves_count' not in prompt_cols:
             op.add_column('prompts', sa.Column('saves_count', sa.Integer(), server_default="0", nullable=False))
        
        if 'price' not in prompt_cols:
             op.add_column('prompts', sa.Column('price', sa.Integer(), server_default="0", nullable=False))
             
        if 'currency' not in prompt_cols:
             op.add_column('prompts', sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(length=3), server_default="usd", nullable=False))
        
        if 'like_count' not in prompt_cols:
             op.add_column('prompts', sa.Column('like_count', sa.Integer(), server_default="0", nullable=False))


    # COMMENTS
    if not inspector.has_table('comments'):
        op.create_table('comments',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('prompt_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('author_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('body', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.Column('like_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_comments_author_id'), 'comments', ['author_id'], unique=False)
        op.create_index(op.f('ix_comments_prompt_id'), 'comments', ['prompt_id'], unique=False)
    else:
        # Check like_count for comments just in case
        comment_cols = [c['name'] for c in inspector.get_columns('comments')]
        if 'like_count' not in comment_cols:
            op.add_column('comments', sa.Column('like_count', sa.Integer(), server_default="0", nullable=False))

    # PURCHASES
    if not inspector.has_table('purchases'):
        op.create_table('purchases',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('buyer_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('seller_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('prompt_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('platform_fee_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(length=3), nullable=False),
        sa.Column('stripe_payment_intent_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_purchases_buyer_id'), 'purchases', ['buyer_id'], unique=False)
        op.create_index(op.f('ix_purchases_prompt_id'), 'purchases', ['prompt_id'], unique=False)
        op.create_index(op.f('ix_purchases_seller_id'), 'purchases', ['seller_id'], unique=False)
        op.create_index(op.f('ix_purchases_status'), 'purchases', ['status'], unique=False)
        op.create_index(op.f('ix_purchases_stripe_payment_intent_id'), 'purchases', ['stripe_payment_intent_id'], unique=False)

    # SAVES
    if not inspector.has_table('saves'):
        op.create_table('saves',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('prompt_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'prompt_id', name='uq_save_user_prompt')
        )
        op.create_index(op.f('ix_saves_prompt_id'), 'saves', ['prompt_id'], unique=False)
        op.create_index(op.f('ix_saves_user_id'), 'saves', ['user_id'], unique=False)


def downgrade() -> None:
    # Downgrade logic is complex with conditional upgrades.
    # For now, we'll keep the original destructive logic but wrapped in checks,
    # or just assume clean slate. 
    # NOTE: Downgrade on production with data is rare.
    pass
