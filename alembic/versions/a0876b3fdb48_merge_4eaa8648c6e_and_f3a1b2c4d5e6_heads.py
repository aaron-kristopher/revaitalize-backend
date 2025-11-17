"""merge 4eaa8648c6e and f3a1b2c4d5e6 heads

Revision ID: a0876b3fdb48
Revises: a43aa8648c6e, f3a1b2c4d5e6
Create Date: 2025-09-18 15:24:33.423584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0876b3fdb48'
down_revision: Union[str, Sequence[str], None] = ('a43aa8648c6e', 'f3a1b2c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
