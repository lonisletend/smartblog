"""add article and category table

Revision ID: ae36b84d0c7c
Revises: 6fcb983a0555
Create Date: 2019-03-14 15:33:31.942960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae36b84d0c7c'
down_revision = '6fcb983a0555'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('is_shown', sa.Integer(), nullable=True),
    sa.Column('is_deleted', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_category_name'), 'category', ['name'], unique=True)
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=True),
    sa.Column('text', sa.String(length=16000000), nullable=True),
    sa.Column('cate_id', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('modified', sa.DateTime(), nullable=True),
    sa.Column('is_topping', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('views', sa.Integer(), nullable=True),
    sa.Column('comments_num', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('is_deleted', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cate_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_created'), 'article', ['created'], unique=False)
    op.create_index(op.f('ix_article_is_topping'), 'article', ['is_topping'], unique=False)
    op.create_index(op.f('ix_article_modified'), 'article', ['modified'], unique=False)
    op.create_index(op.f('ix_article_status'), 'article', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_article_status'), table_name='article')
    op.drop_index(op.f('ix_article_modified'), table_name='article')
    op.drop_index(op.f('ix_article_is_topping'), table_name='article')
    op.drop_index(op.f('ix_article_created'), table_name='article')
    op.drop_table('article')
    op.drop_index(op.f('ix_category_name'), table_name='category')
    op.drop_table('category')
    # ### end Alembic commands ###