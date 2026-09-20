"""Initial migration - create tickets table

Revision ID: 001
Revises: 
Create Date: 2026-09-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('language', sa.String(10), nullable=True),
        sa.Column('customer_id', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='open'),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_tickets_status', 'tickets', ['status'])
    op.create_index('ix_tickets_customer_id', 'tickets', ['customer_id'])
    op.create_index('ix_tickets_created_at', 'tickets', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_tickets_created_at', table_name='tickets')
    op.drop_index('ix_tickets_customer_id', table_name='tickets')
    op.drop_index('ix_tickets_status', table_name='tickets')
    op.drop_table('tickets')