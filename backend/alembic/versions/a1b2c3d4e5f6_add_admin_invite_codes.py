"""add admin invite codes table

Revision ID: a1b2c3d4e5f6
Revises: 0ad52981b691
Create Date: 2026-08-17 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '0ad52981b691'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'admin_invite_codes',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('code', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('used_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_admin_invite_codes_id', 'admin_invite_codes', ['id'], unique=False)
    op.create_index('ix_admin_invite_codes_code', 'admin_invite_codes', ['code'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_admin_invite_codes_code', table_name='admin_invite_codes')
    op.drop_index('ix_admin_invite_codes_id', table_name='admin_invite_codes')
    op.drop_table('admin_invite_codes')
