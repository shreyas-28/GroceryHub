"""empty message

Revision ID: a4f15ca42349
Revises: 1ad881c583ed
Create Date: 2023-07-09 22:36:30.569398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4f15ca42349'
down_revision = '1ad881c583ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles_users')
    op.drop_table('role')
    with op.batch_alter_table('user_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('isAdmin', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('isManager', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_model', schema=None) as batch_op:
        batch_op.drop_column('isManager')
        batch_op.drop_column('isAdmin')

    op.create_table('role',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('roles_users',
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('role_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_model.uuid'], )
    )
    # ### end Alembic commands ###
