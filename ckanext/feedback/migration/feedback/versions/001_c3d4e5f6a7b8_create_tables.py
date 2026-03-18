"""create feedback_rating and feedback_submission tables

Revision ID: c3d4e5f6a7b8
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c3d4e5f6a7b8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'feedback_rating',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('package_id', sa.UnicodeText, nullable=False),
        sa.Column('ip_hash', sa.UnicodeText, nullable=False),
        sa.Column('user_id', sa.UnicodeText, nullable=True),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime),
        sa.UniqueConstraint('package_id', 'ip_hash',
                            name='uq_feedback_rating_pkg_ip'),
    )
    op.create_index('ix_feedback_rating_package_id',
                     'feedback_rating', ['package_id'])

    op.create_table(
        'feedback_submission',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('package_id', sa.UnicodeText, nullable=False),
        sa.Column('user_id', sa.UnicodeText, nullable=True),
        sa.Column('author_name', sa.UnicodeText, nullable=True),
        sa.Column('author_email', sa.UnicodeText, nullable=True),
        sa.Column('subject_type', sa.UnicodeText, nullable=False),
        sa.Column('reason', sa.UnicodeText, nullable=False),
        sa.Column('body', sa.UnicodeText, nullable=False),
        sa.Column('created_at', sa.DateTime),
    )
    op.create_index('ix_feedback_submission_package_id',
                     'feedback_submission', ['package_id'])


def downgrade():
    op.drop_index('ix_feedback_submission_package_id',
                   table_name='feedback_submission')
    op.drop_table('feedback_submission')
    op.drop_index('ix_feedback_rating_package_id',
                   table_name='feedback_rating')
    op.drop_table('feedback_rating')
