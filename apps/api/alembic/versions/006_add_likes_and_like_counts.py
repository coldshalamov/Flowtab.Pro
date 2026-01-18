"""Add likes table and like_count columns

Revision ID: 006
Revises: 005
Create Date: 2026-01-18 16:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add like_count to prompts and comments.
    op.add_column(
        "prompts",
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "comments",
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
    )

    # Create likes table.
    op.create_table(
        "likes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("target_type", sa.String(length=16), nullable=False),
        sa.Column("target_id", sa.String(), nullable=False),
        sa.Column(
            "createdAt",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "target_type",
            "target_id",
            name="uq_like_user_target",
        ),
    )

    op.create_index(op.f("ix_likes_user_id"), "likes", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_likes_target_type"), "likes", ["target_type"], unique=False
    )
    op.create_index(op.f("ix_likes_target_id"), "likes", ["target_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_likes_target_id"), table_name="likes")
    op.drop_index(op.f("ix_likes_target_type"), table_name="likes")
    op.drop_index(op.f("ix_likes_user_id"), table_name="likes")

    op.drop_table("likes")

    op.drop_column("comments", "like_count")
    op.drop_column("prompts", "like_count")
