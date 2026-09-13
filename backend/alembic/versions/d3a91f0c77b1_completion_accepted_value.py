"""completion_suggestion.accepted_value

A reviewer may accept a completion with a correction. Without somewhere to put
the corrected value, `Edit` on a completion would silently commit the bot's
value instead of the human's.

Revision ID: d3a91f0c77b1
Revises: aa17ec104d8d
"""

import sqlalchemy as sa
from alembic import op

revision = "d3a91f0c77b1"
down_revision = "aa17ec104d8d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("completion_suggestion", sa.Column("accepted_value", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("completion_suggestion", "accepted_value")
