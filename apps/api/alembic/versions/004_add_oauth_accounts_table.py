"""Add oauth_accounts table

Revision ID: 004
Revises: 003
Create Date: 2026-01-18 15:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if not inspector.has_table("oauth_accounts"):
        op.create_table(
            "oauth_accounts",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=False),
            sa.Column("provider", sa.String(length=32), nullable=False),
            sa.Column("provider_user_id", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=True),
            sa.Column("name", sa.String(length=255), nullable=True),
            sa.Column(
                "createdAt",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "provider",
                "provider_user_id",
                name="uq_oauth_provider_user",
            ),
        )

        op.create_index(
            op.f("ix_oauth_accounts_user_id"), "oauth_accounts", ["user_id"], unique=False
        )
        op.create_index(
            op.f("ix_oauth_accounts_provider"), "oauth_accounts", ["provider"], unique=False
        )
        op.create_index(
            op.f("ix_oauth_accounts_provider_user_id"),
            "oauth_accounts",
            ["provider_user_id"],
            unique=False,
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if inspector.has_table("oauth_accounts"):
        op.drop_index(
            op.f("ix_oauth_accounts_provider_user_id"), table_name="oauth_accounts"
        )
        op.drop_index(op.f("ix_oauth_accounts_provider"), table_name="oauth_accounts")
        op.drop_index(op.f("ix_oauth_accounts_user_id"), table_name="oauth_accounts")
        op.drop_table("oauth_accounts")
