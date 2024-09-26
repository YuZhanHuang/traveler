"""創建order與address

Revision ID: 3d60391e197a
Revises: 
Create Date: 2024-09-25 02:47:03.613068

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3d60391e197a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('order',
                    sa.Column('uid', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('id', sa.String(length=8), nullable=False),
                    sa.Column('name', sa.Text(), nullable=False, comment='訂單名稱'),
                    sa.Column('price', sa.Numeric(precision=18, scale=2), nullable=False, comment='訂單價格'),
                    sa.Column('currency', sa.String(length=3), nullable=False, comment='貨幣代碼'),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('updated', sa.DateTime(), nullable=True),
                    sa.Column('deleted', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('uid')
                    )
    op.create_table('address',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('order_id', sa.Integer(), nullable=False),
                    sa.Column('city', sa.Text(), nullable=False, comment='城市'),
                    sa.Column('district', sa.Text(), nullable=False, comment='區域'),
                    sa.Column('street', sa.Text(), nullable=False, comment='街道'),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('updated', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['order_id'], ['order.uid'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('address')
    op.drop_table('order')
