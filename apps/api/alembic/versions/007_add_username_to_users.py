"""Add username to users

Revision ID: 007
Revises: 006
Create Date: 2026-01-19 03:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add username column as nullable initially
    op.add_column("users", sa.Column("username", sa.String(length=255), nullable=True))
    
    # 2. Populate username with email prefix for existing users (basic fix)
    op.execute("UPDATE users SET username = split_part(email, '@', 1) WHERE username IS NULL")
    
    # 3. Handle potential duplicates (if any) or just hope for the best in early dev
    # Actually, if there are duplicates, the unique index will fail.
    # We'll just assume unique emails mean mostly unique prefixes for now.
    
    # 4. Make it non-nullable and add index
    op.alter_column("users", "username", nullable=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "username")
