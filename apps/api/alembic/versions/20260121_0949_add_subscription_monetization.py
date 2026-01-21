"""Add subscription monetization tables

Revision ID: 20260121_0949
Revises: 20260119_0607_79a4be091917
Create Date: 2026-01-21 09:49:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260121_0949'
down_revision = '79a4be091917'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add subscription-related fields to users table
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_creator', sa.Boolean(), server_default='false', nullable=False))
    op.create_index('idx_users_stripe_customer', 'users', ['stripe_customer_id'])
    op.create_index(
        'idx_users_stripe_connect',
        'users',
        ['stripe_connect_id'],
        postgresql_where=sa.text('stripe_connect_id IS NOT NULL')
    )

    # Add premium/featured flags to prompts table
    op.add_column('prompts', sa.Column('is_premium', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('prompts', sa.Column('featured', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('prompts', sa.Column('total_copies', sa.Integer(), server_default='0', nullable=False))
    op.create_index('idx_prompts_premium', 'prompts', ['is_premium', 'featured'])

    # Create subscriptions table
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

    # Create flow_copies table (append-only log)
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

    # Create creator_payouts table
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
    # Drop tables
    op.drop_table('creator_payouts')
    op.drop_table('flow_copies')
    op.drop_table('subscriptions')

    # Remove columns from prompts
    op.drop_index('idx_prompts_premium', table_name='prompts')
    op.drop_column('prompts', 'total_copies')
    op.drop_column('prompts', 'featured')
    op.drop_column('prompts', 'is_premium')

    # Remove columns from users
    op.drop_index('idx_users_stripe_connect', table_name='users')
    op.drop_index('idx_users_stripe_customer', table_name='users')
    op.drop_column('users', 'is_creator')
    op.drop_column('users', 'stripe_customer_id')
