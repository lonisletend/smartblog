"""添加访问记录表

Revision ID: 22a615044aa6
Revises: dd11de3b7bd2
Create Date: 2019-04-26 16:21:44.342770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22a615044aa6'
down_revision = 'dd11de3b7bd2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('art_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('ip', sa.String(length=32), nullable=True),
    sa.Column('platform', sa.String(length=32), nullable=True),
    sa.Column('browser', sa.String(length=32), nullable=True),
    sa.Column('version', sa.String(length=32), nullable=True),
    sa.Column('language', sa.String(length=32), nullable=True),
    sa.Column('is_deleted', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_record_art_id'), 'record', ['art_id'], unique=False)
    op.create_index(op.f('ix_record_time'), 'record', ['time'], unique=False)
    op.create_index(op.f('ix_record_user_id'), 'record', ['user_id'], unique=False)
    op.drop_table('sqlite_stat1')
    op.drop_table('sqlite_stat4')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sqlite_stat4',
    sa.Column('tbl', sa.NullType(), nullable=True),
    sa.Column('idx', sa.NullType(), nullable=True),
    sa.Column('neq', sa.NullType(), nullable=True),
    sa.Column('nlt', sa.NullType(), nullable=True),
    sa.Column('ndlt', sa.NullType(), nullable=True),
    sa.Column('sample', sa.NullType(), nullable=True)
    )
    op.create_table('sqlite_stat1',
    sa.Column('tbl', sa.NullType(), nullable=True),
    sa.Column('idx', sa.NullType(), nullable=True),
    sa.Column('stat', sa.NullType(), nullable=True)
    )
    op.drop_index(op.f('ix_record_user_id'), table_name='record')
    op.drop_index(op.f('ix_record_time'), table_name='record')
    op.drop_index(op.f('ix_record_art_id'), table_name='record')
    op.drop_table('record')
    # ### end Alembic commands ###
