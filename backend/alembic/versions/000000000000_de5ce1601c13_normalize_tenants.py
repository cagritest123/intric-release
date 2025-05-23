"""normalize tenants
Revision ID: de5ce1601c13
Revises: 3956e5dc413f
Create Date: 2023-11-29 15:25:37.023361
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic
revision = 'de5ce1601c13'
down_revision = '3956e5dc413f'
branch_labels = None
depends_on = None

GET_TENANT = "SELECT id, tenant FROM users"
INSERT_INTO_TENANT = "INSERT INTO tenants (name) VALUES (:name) RETURNING id, name"
UPDATE_USER = "UPDATE users SET tenant_id = (:tenant_id) WHERE tenant = :tenant"
UPDATE_GROUP = "UPDATE groups SET tenant_id = (:tenant_id) WHERE user_id = :user_id"
SET_ALL_GROUPS_PRIVATE = "UPDATE groups SET is_public = false"
GET_TENANT_NAMES = "SELECT id, name FROM tenants"
SET_TENANT_STRING = "UPDATE users SET tenant = (:tenant) WHERE tenant_id = :tenant_id"


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()

    op.create_table(
        'tenants',
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
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'uuid',
            postgresql.UUID(),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('name', sa.Text(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tenants_id'), 'tenants', ['id'], unique=False)
    op.create_index(op.f('ix_tenants_uuid'), 'tenants', ['uuid'], unique=True)
    op.add_column('groups', sa.Column('is_public', sa.Boolean(), nullable=True))
    op.add_column('groups', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_groups_tenant_id'), 'groups', ['tenant_id'], unique=False)
    op.create_foreign_key('group_tenant_fk', 'groups', 'tenants', ['tenant_id'], ['id'])
    op.add_column('users', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'users_tenants_fk',
        'users',
        'tenants',
        ['tenant_id'],
        ['id'],
        ondelete='CASCADE',
    )

    conn.execute(sa.text(SET_ALL_GROUPS_PRIVATE))

    user_tenants = conn.execute(sa.text(GET_TENANT)).fetchall()
    unique_tenants = set([t[1] for t in user_tenants])

    for tenant in unique_tenants:
        res = conn.execute(
            sa.text(INSERT_INTO_TENANT), parameters={"name": tenant}
        ).fetchall()[0]

        conn.execute(
            sa.text(UPDATE_USER), parameters={"tenant_id": res[0], "tenant": res[1]}
        )

        for user_tenant in user_tenants:
            if user_tenant[1] == res[1]:
                conn.execute(
                    sa.text(UPDATE_GROUP),
                    parameters={"tenant_id": res[0], "user_id": user_tenant[0]},
                )

    op.drop_column('users', 'tenant')
    op.alter_column('users', 'tenant_id', nullable=False)
    op.alter_column('groups', 'tenant_id', nullable=False)
    op.alter_column('groups', 'is_public', nullable=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'users', sa.Column('tenant', sa.TEXT(), autoincrement=False, nullable=True)
    )

    conn = op.get_bind()
    tenants = conn.execute(sa.text(GET_TENANT_NAMES)).fetchall()
    for tenant in tenants:
        conn.execute(
            sa.text(SET_TENANT_STRING),
            parameters={"tenant": tenant[1], "tenant_id": tenant[0]},
        )

    op.alter_column('users', 'tenant', nullable=False)

    op.drop_constraint('users_tenants_fk', 'users', type_='foreignkey')
    op.drop_column('users', 'tenant_id')
    op.drop_constraint('group_tenant_fk', 'groups', type_='foreignkey')
    op.drop_index(op.f('ix_groups_tenant_id'), table_name='groups')
    op.drop_column('groups', 'tenant_id')
    op.drop_column('groups', 'is_public')
    op.drop_index(op.f('ix_tenants_uuid'), table_name='tenants')
    op.drop_index(op.f('ix_tenants_id'), table_name='tenants')
    op.drop_table('tenants')
    # ### end Alembic commands ###
