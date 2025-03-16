"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}


# alembic/versions/20250302_initial_migration.py
"""Initial migration

Revision ID: 7f9c43f51c77
Revises: 
Create Date: 2025-03-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from enum import Enum as PyEnum

# revision identifiers, used by Alembic.
revision = '7f9c43f51c77'
down_revision = None
branch_labels = None
depends_on = None


# Enumクラスの定義
class UserRoleEnum(PyEnum):
    ARTIST = "artist"
    LISTENER = "listener"
    ADMIN = "admin"


class PaymentMethodEnum(PyEnum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class PurchaseStatusEnum(PyEnum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"


def upgrade():
    # ユーザーテーブルの作成
    op.create_table(
        'user',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('firebase_uid', sa.String(), nullable=False