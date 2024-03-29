"""empty message

Revision ID: 16ab11413f40
Revises: 3deaceb9166a
Create Date: 2023-08-09 00:47:23.783669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16ab11413f40'
down_revision = '3deaceb9166a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('engagement', sa.Integer(), nullable=True))
        batch_op.drop_column('popularity')

    with op.batch_alter_table('section_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('engagement', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('section_model', schema=None) as batch_op:
        batch_op.drop_column('engagement')

    with op.batch_alter_table('product_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('popularity', sa.INTEGER(), nullable=True))
        batch_op.drop_column('engagement')

    # ### end Alembic commands ###
