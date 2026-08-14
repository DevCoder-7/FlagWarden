"""initial FlagWarden 2.0 schema
Revision ID: 0001_initial
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_user_id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(128)),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("streak", sa.Integer(), nullable=False),
        sa.Column("active_challenge_id", sa.String(128)),
        sa.Column("last_solved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("telegram_user_id"),
    )
    op.create_index("ix_users_telegram_user_id", "users", ["telegram_user_id"])
    op.create_table(
        "processed_updates",
        sa.Column("update_id", sa.Integer(), primary_key=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "challenge_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("challenge_id", sa.String(128), nullable=False),
        sa.Column("solved", sa.Boolean(), nullable=False),
        sa.Column("hints_used", sa.Integer(), nullable=False),
        sa.Column("score_awarded", sa.Integer(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("solved_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("user_id", "challenge_id", name="uq_progress_user_challenge"),
    )
    op.create_index("ix_challenge_progress_user_id", "challenge_progress", ["user_id"])
    op.create_index("ix_challenge_progress_challenge_id", "challenge_progress", ["challenge_id"])
    op.create_table(
        "skill_mastery",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("skill", sa.String(128), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "skill", name="uq_mastery_user_skill"),
    )
    op.create_index("ix_skill_mastery_user_id", "skill_mastery", ["user_id"])
    op.create_index("ix_skill_mastery_skill", "skill_mastery", ["skill"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(96), nullable=False),
        sa.Column("actor_telegram_id", sa.Integer()),
        sa.Column("object_id", sa.String(160)),
        sa.Column("details_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_events_event_type", "audit_events", ["event_type"])
    op.create_index("ix_audit_events_actor_telegram_id", "audit_events", ["actor_telegram_id"])
    op.create_table(
        "challenge_drafts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenge_id", sa.String(128), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("author_telegram_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_telegram_id", sa.Integer()),
        sa.Column("content_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_challenge_drafts_challenge_id", "challenge_drafts", ["challenge_id"])
    op.create_index("ix_challenge_drafts_status", "challenge_drafts", ["status"])
    op.create_index(
        "ix_challenge_drafts_author_telegram_id", "challenge_drafts", ["author_telegram_id"]
    )


def downgrade():
    op.drop_table("challenge_drafts")
    op.drop_table("audit_events")
    op.drop_table("skill_mastery")
    op.drop_table("challenge_progress")
    op.drop_table("processed_updates")
    op.drop_table("users")
