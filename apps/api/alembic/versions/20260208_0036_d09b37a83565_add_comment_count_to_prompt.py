"""Add comment_count to Prompt

Revision ID: d09b37a83565
Revises: 20260121_0949
Create Date: 2026-02-08 00:36:12.717200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'd09b37a83565'
down_revision: Union[str, None] = '20260121_0949'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _safe_drop_index(index_name: str, table_name: str):
    """Safely drop an index if it exists."""
    try:
        op.drop_index(op.f(index_name), table_name=table_name)
    except Exception:
        pass  # Index doesn't exist, that's fine


def _safe_drop_constraint(constraint_name, table_name: str, type_: str):
    """Safely drop a constraint if it exists."""
    try:
        op.drop_constraint(constraint_name, table_name, type_=type_)
    except Exception:
        pass  # Constraint doesn't exist, that's fine


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # ========== NEW TABLES (with existence checks) ==========

    # PROVIDERS table
    if not inspector.has_table('providers'):
        op.create_table('providers',
            sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
            sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
            sa.Column('display_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
            sa.Column('supports_api_key', sa.Boolean(), nullable=False),
            sa.Column('supports_oauth', sa.Boolean(), nullable=False),
            sa.Column('supports_manual', sa.Boolean(), nullable=False),
            sa.Column('api_endpoint', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
            sa.Column('auth_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
            sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
            sa.Column('documentation_url', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
            sa.Column('rate_limit_per_minute', sa.Integer(), nullable=True),
            sa.Column('rate_limit_per_hour', sa.Integer(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_providers_name'), 'providers', ['name'], unique=True)
        op.create_index(op.f('ix_providers_slug'), 'providers', ['slug'], unique=True)

    # ACCOUNT_CONNECTIONS table
    if not inspector.has_table('account_connections'):
        op.create_table('account_connections',
            sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('provider_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('label', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
            sa.Column('connection_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
            sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
            sa.Column('last_used_at', sa.DateTime(), nullable=True),
            sa.Column('last_error', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_account_connections_connection_type'), 'account_connections', ['connection_type'], unique=False)
        op.create_index(op.f('ix_account_connections_provider_id'), 'account_connections', ['provider_id'], unique=False)
        op.create_index(op.f('ix_account_connections_status'), 'account_connections', ['status'], unique=False)
        op.create_index(op.f('ix_account_connections_user_id'), 'account_connections', ['user_id'], unique=False)

    # CREDENTIAL_VAULT_ITEMS table
    if not inspector.has_table('credential_vault_items'):
        op.create_table('credential_vault_items',
            sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('connection_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('encrypted_data', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('key_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['connection_id'], ['account_connections.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_credential_vault_items_connection_id'), 'credential_vault_items', ['connection_id'], unique=False)

    # MANUAL_OVERRIDES table
    if not inspector.has_table('manual_overrides'):
        op.create_table('manual_overrides',
            sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('connection_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('config', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['connection_id'], ['account_connections.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_manual_overrides_connection_id'), 'manual_overrides', ['connection_id'], unique=False)

    # ========== PROMPTS - add comment_count column ==========
    prompt_cols = [c['name'] for c in inspector.get_columns('prompts')]
    if 'comment_count' not in prompt_cols:
        op.add_column('prompts', sa.Column('comment_count', sa.Integer(), server_default='0', nullable=False))

    # ========== INDEX MIGRATIONS (safe operations) ==========
    # These are index renames/recreations - use safe drops

    # creator_payouts indexes
    _safe_drop_index('idx_payouts_creator', 'creator_payouts')
    _safe_drop_index('idx_payouts_status', 'creator_payouts')

    existing_cp_indexes = [i['name'] for i in inspector.get_indexes('creator_payouts')]
    if 'ix_creator_payouts_creator_id' not in existing_cp_indexes:
        try:
            op.create_index(op.f('ix_creator_payouts_creator_id'), 'creator_payouts', ['creator_id'], unique=False)
        except Exception:
            pass

    # flow_copies indexes
    _safe_drop_index('idx_copies_billing', 'flow_copies')
    _safe_drop_index('idx_copies_creator', 'flow_copies')
    _safe_drop_index('idx_copies_user_month', 'flow_copies')

    existing_fc_indexes = [i['name'] for i in inspector.get_indexes('flow_copies')]
    if 'ix_flow_copies_creator_id' not in existing_fc_indexes:
        try:
            op.create_index(op.f('ix_flow_copies_creator_id'), 'flow_copies', ['creator_id'], unique=False)
        except Exception:
            pass
    if 'ix_flow_copies_flow_id' not in existing_fc_indexes:
        try:
            op.create_index(op.f('ix_flow_copies_flow_id'), 'flow_copies', ['flow_id'], unique=False)
        except Exception:
            pass
    if 'ix_flow_copies_user_id' not in existing_fc_indexes:
        try:
            op.create_index(op.f('ix_flow_copies_user_id'), 'flow_copies', ['user_id'], unique=False)
        except Exception:
            pass

    # prompts indexes
    _safe_drop_index('idx_prompts_premium', 'prompts')

    # subscriptions indexes
    _safe_drop_index('idx_subscriptions_status', 'subscriptions')
    _safe_drop_index('idx_subscriptions_stripe', 'subscriptions')

    existing_sub_indexes = [i['name'] for i in inspector.get_indexes('subscriptions')]
    if 'ix_subscriptions_status' not in existing_sub_indexes:
        try:
            op.create_index(op.f('ix_subscriptions_status'), 'subscriptions', ['status'], unique=False)
        except Exception:
            pass
    if 'ix_subscriptions_stripe_subscription_id' not in existing_sub_indexes:
        try:
            op.create_index(op.f('ix_subscriptions_stripe_subscription_id'), 'subscriptions', ['stripe_subscription_id'], unique=False)
        except Exception:
            pass
    if 'ix_subscriptions_user_id' not in existing_sub_indexes:
        try:
            op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)
        except Exception:
            pass

    # users indexes
    _safe_drop_index('idx_users_stripe_connect', 'users')
    _safe_drop_index('idx_users_stripe_customer', 'users')

    existing_user_indexes = [i['name'] for i in inspector.get_indexes('users')]
    if 'ix_users_stripe_customer_id' not in existing_user_indexes:
        try:
            op.create_index(op.f('ix_users_stripe_customer_id'), 'users', ['stripe_customer_id'], unique=False)
        except Exception:
            pass


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # users indexes
    _safe_drop_index('ix_users_stripe_customer_id', 'users')
    try:
        op.create_index(op.f('idx_users_stripe_customer'), 'users', ['stripe_customer_id'], unique=False)
    except Exception:
        pass
    try:
        op.create_index(op.f('idx_users_stripe_connect'), 'users', ['stripe_connect_id'], unique=False)
    except Exception:
        pass

    # subscriptions indexes
    _safe_drop_index('ix_subscriptions_user_id', 'subscriptions')
    _safe_drop_index('ix_subscriptions_stripe_subscription_id', 'subscriptions')
    _safe_drop_index('ix_subscriptions_status', 'subscriptions')
    try:
        op.create_index(op.f('idx_subscriptions_stripe'), 'subscriptions', ['stripe_subscription_id'], unique=False)
    except Exception:
        pass
    try:
        op.create_index(op.f('idx_subscriptions_status'), 'subscriptions', ['status'], unique=False)
    except Exception:
        pass

    # prompts
    try:
        op.create_index(op.f('idx_prompts_premium'), 'prompts', ['is_premium', 'featured'], unique=False)
    except Exception:
        pass
    
    prompt_cols = [c['name'] for c in inspector.get_columns('prompts')]
    if 'comment_count' in prompt_cols:
        op.drop_column('prompts', 'comment_count')

    # flow_copies indexes
    _safe_drop_index('ix_flow_copies_user_id', 'flow_copies')
    _safe_drop_index('ix_flow_copies_flow_id', 'flow_copies')
    _safe_drop_index('ix_flow_copies_creator_id', 'flow_copies')
    try:
        op.create_index(op.f('idx_copies_user_month'), 'flow_copies', ['user_id', 'billing_month'], unique=False)
    except Exception:
        pass
    try:
        op.create_index(op.f('idx_copies_creator'), 'flow_copies', ['creator_id', 'billing_month'], unique=False)
    except Exception:
        pass
    try:
        op.create_index(op.f('idx_copies_billing'), 'flow_copies', ['billing_month', 'counted_for_payout'], unique=False)
    except Exception:
        pass

    # creator_payouts indexes
    _safe_drop_index('ix_creator_payouts_creator_id', 'creator_payouts')
    try:
        op.create_index(op.f('idx_payouts_status'), 'creator_payouts', ['status', 'billing_month'], unique=False)
    except Exception:
        pass
    try:
        op.create_index(op.f('idx_payouts_creator'), 'creator_payouts', ['creator_id', 'billing_month'], unique=False)
    except Exception:
        pass

    # Drop new tables
    if inspector.has_table('manual_overrides'):
        _safe_drop_index('ix_manual_overrides_connection_id', 'manual_overrides')
        op.drop_table('manual_overrides')
    
    if inspector.has_table('credential_vault_items'):
        _safe_drop_index('ix_credential_vault_items_connection_id', 'credential_vault_items')
        op.drop_table('credential_vault_items')
    
    if inspector.has_table('account_connections'):
        _safe_drop_index('ix_account_connections_user_id', 'account_connections')
        _safe_drop_index('ix_account_connections_status', 'account_connections')
        _safe_drop_index('ix_account_connections_provider_id', 'account_connections')
        _safe_drop_index('ix_account_connections_connection_type', 'account_connections')
        op.drop_table('account_connections')
    
    if inspector.has_table('providers'):
        _safe_drop_index('ix_providers_slug', 'providers')
        _safe_drop_index('ix_providers_name', 'providers')
        op.drop_table('providers')
