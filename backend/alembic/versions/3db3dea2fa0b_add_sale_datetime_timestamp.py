"""add sale_datetime timestamp

Adds a timezone-aware sale_datetime column to sales, backward-compatible
with the existing date-only sale_date column (which is preserved, not
dropped). For rows that predate this migration, sale_datetime is backfilled
from sale_date using a fixed fallback time of 12:00:00 in the application's
business timezone (Asia/Dhaka, UTC+06:00) -- chosen because it doesn't bias
any hour-of-day/time-of-day analytics toward the start or end of a business
day. Backfilled rows are flagged via is_estimated_time=True so the
data-quality panel can report real timestamp coverage instead of treating
guessed values as equally trustworthy as captured ones.

Revision ID: 3db3dea2fa0b
Revises: 928219e551cd
Create Date: 2026-08-16 18:15:12.932128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3db3dea2fa0b'
down_revision: Union[str, Sequence[str], None] = '928219e551cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Fallback time-of-day (in Asia/Dhaka, UTC+06:00) applied to legacy date-only records.
DHAKA_FALLBACK_OFFSET = "+06:00"
DHAKA_FALLBACK_TIME = "12:00:00"


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add columns as nullable first so existing rows aren't rejected.
    op.add_column('sales', sa.Column('sale_datetime', sa.DateTime(timezone=True), nullable=True))
    op.add_column('sales', sa.Column('is_estimated_time', sa.Boolean(), nullable=False, server_default=sa.false()))

    # 2. Backfill sale_datetime for pre-existing rows from sale_date + fixed fallback time,
    #    and mark those rows as estimated (their real time-of-day was never captured).
    op.execute(
        f"""
        UPDATE sales
        SET sale_datetime = (sale_date::text || ' {DHAKA_FALLBACK_TIME}{DHAKA_FALLBACK_OFFSET}')::timestamptz,
            is_estimated_time = TRUE
        WHERE sale_datetime IS NULL
        """
    )

    # 3. Now that every row has a value, enforce NOT NULL and drop the server default
    #    (new rows must supply sale_datetime explicitly going forward).
    op.alter_column('sales', 'sale_datetime', nullable=False)
    op.alter_column('sales', 'is_estimated_time', server_default=None)

    op.create_index('idx_sales_sale_datetime', 'sales', ['sale_datetime'], unique=False)
    op.create_index(op.f('ix_sales_sale_datetime'), 'sales', ['sale_datetime'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_sales_sale_datetime'), table_name='sales')
    op.drop_index('idx_sales_sale_datetime', table_name='sales')
    op.drop_column('sales', 'is_estimated_time')
    op.drop_column('sales', 'sale_datetime')
