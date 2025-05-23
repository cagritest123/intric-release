"""add template_id columns
Revision ID: a19994071e35
Revises: 80c7388d88d3
Create Date: 2024-12-18 16:56:23.517431
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = "a19994071e35"
down_revision = "80c7388d88d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("apps", sa.Column("template_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "apps_template_id_fkey",
        "apps",
        "app_templates",
        ["template_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column(
        "assistant_templates",
        "prompt_text",
        existing_type=sa.TEXT(),
        type_=sa.String(),
        existing_nullable=True,
    )
    op.add_column("assistants", sa.Column("template_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "assistants_template_id_fkey",
        "assistants",
        "assistant_templates",
        ["template_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("assistants_template_id_fkey", "assistants", type_="foreignkey")
    op.drop_column("assistants", "template_id")
    op.alter_column(
        "assistant_templates",
        "prompt_text",
        existing_type=sa.String(),
        type_=sa.TEXT(),
        existing_nullable=True,
    )
    op.drop_constraint("apps_template_id_fkey", "apps", type_="foreignkey")
    op.drop_column("apps", "template_id")
    # ### end Alembic commands ###
