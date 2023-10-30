"""Added Workspace and WorkspaceUserMapping models

Revision ID: 3b7943030024
Revises: bf303020c450
Create Date: 2023-10-31 04:12:54.344918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b7943030024'
down_revision: Union[str, None] = 'bf303020c450'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workspaces',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('hashed_api_key', sa.String(), nullable=True),
    sa.Column('hashed_api_secret', sa.String(), nullable=True),
    sa.Column('create_datetime', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('update_datetime', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspaces_id'), 'workspaces', ['id'], unique=False)
    op.create_index(op.f('ix_workspaces_name'), 'workspaces', ['name'], unique=False)
    op.create_table('workspace_user_mapping',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workspace_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.Enum('owner', 'editor', name='role_enum'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspace_user_mapping_id'), 'workspace_user_mapping', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_workspace_user_mapping_id'), table_name='workspace_user_mapping')
    op.drop_table('workspace_user_mapping')
    op.drop_index(op.f('ix_workspaces_name'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_id'), table_name='workspaces')
    op.drop_table('workspaces')
    # ### end Alembic commands ###
