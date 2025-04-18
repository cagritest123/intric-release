"""add crawl table
Revision ID: a05ebf86dfed
Revises: 0233c0d35970
Create Date: 2024-04-30 14:09:05.699543
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = 'a05ebf86dfed'
down_revision = '0233c0d35970'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'crawls',
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('allowed_path', sa.String(), nullable=True),
        sa.Column('download_files', sa.Boolean(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column(
            'id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False
        ),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.uuid'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('crawls')
    # ### end Alembic commands ###
