"""Add subscription monetization tables

Revision ID: 20260121_0949
Revises: 20260119_0607_79a4be091917
Create Date: 2026-01-21 09:49:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20260121_0949'
down_revision = '79a4be091917'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # 1. USERS columns
    user_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'stripe_customer_id' not in user_cols:
        op.add_column('users', sa.Column('stripe_customer_id', sa.String(), nullable=True))
        op.create_index('idx_users_stripe_customer', 'users', ['stripe_customer_id'])
    
    if 'is_creator' not in user_cols:
        op.add_column('users', sa.Column('is_creator', sa.Boolean(), server_default='false', nullable=False))

    # Check for stripe_connect_id index if not exists (it might have been created in 79a)
    # The file tries to creating 'idx_users_stripe_connect' for 'stripe_connect_id'.
    # 79a created 'ix_users_stripe_connect_id'. This file creates 'idx_users_stripe_connect'.
    # We should check if index exists to avoid duplication or error.
    indexes = inspector.get_indexes('users')
    index_names = [i['name'] for i in indexes]
    if 'idx_users_stripe_connect' not in index_names:
        # verify column exists first (it should from 79a)
        if 'stripe_connect_id' in user_cols:
            op.create_index(
                'idx_users_stripe_connect',
                'users',
                ['stripe_connect_id'],
                postgresql_where=sa.text('stripe_connect_id IS NOT NULL')
            )

    # 2. PROMPTS columns
    prompt_cols = [c['name'] for c in inspector.get_columns('prompts')]
    if 'is_premium' not in prompt_cols:
        op.add_column('prompts', sa.Column('is_premium', sa.Boolean(), server_default='true', nullable=False))
    if 'featured' not in prompt_cols:
        op.add_column('prompts', sa.Column('featured', sa.Boolean(), server_default='false', nullable=False))
    if 'total_copies' not in prompt_cols:
        op.add_column('prompts', sa.Column('total_copies', sa.Integer(), server_default='0', nullable=False))
    
    # Check index on prompts
    p_indexes = [i['name'] for i in inspector.get_indexes('prompts')]
    if 'idx_prompts_premium' not in p_indexes:
         op.create_index('idx_prompts_premium', 'prompts', ['is_premium', 'featured'])

    # 3. SUBSCRIPTIONS table
    if not inspector.has_table('subscriptions'):
        op.create_table(
            'subscriptions',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('stripe_subscription_id', sa.String(), nullable=False),
            sa.Column('stripe_customer_id', sa.String(), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('plan_id', sa.String(length=50), server_default='premium_monthly', nullable=False),
            sa.Column('current_period_start', sa.DateTime(), nullable=False),
            sa.Column('current_period_end', sa.DateTime(), nullable=False),
            sa.Column('cancel_at_period_end', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('stripe_subscription_id', name='uq_subscription_stripe_id'),
            sa.UniqueConstraint('user_id', name='uq_subscription_user')
        )
        op.create_index('idx_subscriptions_stripe', 'subscriptions', ['stripe_subscription_id'])
        op.create_index('idx_subscriptions_status', 'subscriptions', ['status'])

    # 4. FLOW_COPIES table
    if not inspector.has_table('flow_copies'):
        op.create_table(
            'flow_copies',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('flow_id', sa.String(), nullable=False),
            sa.Column('creator_id', sa.String(), nullable=False),
            sa.Column('counted_for_payout', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('copied_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('billing_month', sa.Date(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['flow_id'], ['prompts.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'flow_id', 'billing_month', name='uq_copy_user_flow_month')
        )
        op.create_index('idx_copies_billing', 'flow_copies', ['billing_month', 'counted_for_payout'])
        op.create_index(
            'idx_copies_creator',
            'flow_copies',
            ['creator_id', 'billing_month'],
            postgresql_where=sa.text('counted_for_payout = true')
        )
        op.create_index(
            'idx_copies_user_month',
            'flow_copies',
            ['user_id', 'billing_month'],
            postgresql_where=sa.text('counted_for_payout = true')
        )

    # 5. CREATOR_PAYOUTS table
    if not inspector.has_table('creator_payouts'):
        op.create_table(
            'creator_payouts',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('creator_id', sa.String(), nullable=False),
            sa.Column('billing_month', sa.Date(), nullable=False),
            sa.Column('copy_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('amount_cents', sa.Integer(), server_default='0', nullable=False),
            sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
            sa.Column('stripe_transfer_id', sa.String(), nullable=True),
            sa.Column('paid_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('creator_id', 'billing_month', name='uq_payout_creator_month')
        )
        op.create_index('idx_payouts_status', 'creator_payouts', ['status', 'billing_month'])
        op.create_index('idx_payouts_creator', 'creator_payouts', ['creator_id', 'billing_month'])


def downgrade() -> None:
    # Basic downgrade checks if elements exist before dropping
    conn = op.get_bind()
    inspector = inspect(conn)

    if inspector.has_table('creator_payouts'):
        op.drop_table('creator_payouts')
    if inspector.has_table('flow_copies'):
        op.drop_table('flow_copies')
    if inspector.has_table('subscriptions'):
        op.drop_table('subscriptions')

    # Columns
    prompt_cols = [c['name'] for c in inspector.get_columns('prompts')]
    if 'total_copies' in prompt_cols: op.drop_column('prompts', 'total_copies')
    if 'featured' in prompt_cols: op.drop_column('prompts', 'featured')
    if 'is_premium' in prompt_cols: op.drop_column('prompts', 'is_premium')

    user_cols = [c['name'] for c in inspector.get_columns('users')]
    # drop index if exists ... simpler to just try/fail or check carefully.
    # We will skip verifying every single index drop for now on downgrade.
    if 'is_creator' in user_cols: op.drop_column('users', 'is_creator')
    if 'stripe_customer_id' in user_cols: op.drop_column('users', 'stripe_customer_id')
