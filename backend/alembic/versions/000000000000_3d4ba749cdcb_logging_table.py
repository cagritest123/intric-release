"""logging table
Revision ID: 3d4ba749cdcb
Revises: 7bcc05803774
Create Date: 2023-12-13 19:13:04.628168
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = '3d4ba749cdcb'
down_revision = '7bcc05803774'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'logging',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('context', sa.String(), nullable=True),
        sa.Column(
            'model_kwargs', postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column('json_body', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('logging')
    # ### end Alembic commands ###
