"""Add author_id to prompts

Revision ID: 003
Revises: 002
Create Date: 2026-01-18 12:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns("prompts")]
    
    if "author_id" not in columns:
        op.add_column("prompts", sa.Column("author_id", sa.String(), nullable=True))
        op.create_foreign_key(None, "prompts", "users", ["author_id"], ["id"])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns("prompts")]
    
    if "author_id" in columns:
        op.drop_constraint(None, "prompts", type_="foreignkey")
        op.drop_column("prompts", "author_id")
