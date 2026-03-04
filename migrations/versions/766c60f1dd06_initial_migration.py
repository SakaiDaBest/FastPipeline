from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '766c60f1dd06'
down_revision: Union[str, Sequence[str], None] = 'afc38ceea1cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new JSONB columns
    op.add_column(
        'pipelines',
        sa.Column('source_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}')
    )

    op.add_column(
        'pipelines',
        sa.Column('destination_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}')
    )

    op.add_column(
        'pipelines',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'))
    )

    # Remove old column
    op.drop_column('pipelines', 'source_path')


def downgrade() -> None:
    # Recreate old column
    op.add_column(
        'pipelines',
        sa.Column('source_path', sa.String(), nullable=True)
    )

    # Remove new columns
    op.drop_column('pipelines', 'is_active')
    op.drop_column('pipelines', 'destination_config')
    op.drop_column('pipelines', 'source_config')
