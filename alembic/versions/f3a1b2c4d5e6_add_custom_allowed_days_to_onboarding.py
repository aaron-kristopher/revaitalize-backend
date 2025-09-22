"""add custom_allowed_days to onboarding

Revision ID: f3a1b2c4d5e6
Revises: 8cd695e7da3c
Create Date: 2025-09-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f3a1b2c4d5e6"
down_revision = "8cd695e7da3c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the nullable integer[] column
    op.add_column(
        "onboarding",
        sa.Column("custom_allowed_days", postgresql.ARRAY(sa.Integer()), nullable=True),
    )

    # CHECK: custom_allowed_days must be subset of {0,1,2,3,4,5,6}
    # Uses Postgres array subset operator <@
    op.create_check_constraint(
        constraint_name="ck_onboarding_custom_allowed_days_range",
        table_name="onboarding",
        condition=sa.text(
            "custom_allowed_days IS NULL OR custom_allowed_days <@ ARRAY[0,1,2,3,4,5,6]::int[]"
        ),
    )


def downgrade() -> None:
    # Drop CHECK constraint first, then the column
    op.drop_constraint(
        "ck_onboarding_custom_allowed_days_range", "onboarding", type_="check"
    )
    op.drop_column("onboarding", "custom_allowed_days") 