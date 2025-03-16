# alembic/versions/20250302_initial_migration.py（続き）
def upgrade():
    # ユーザーテーブルの作成
    op.create_table(
        'user',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('firebase_uid', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('profile_image', sa.String(), nullable=True),
        sa.Column('user_role', sa.Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.LISTENER),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    # 楽曲テーブルの作成
    op.create_table(
        'track',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('artist_id', sa.String(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('genre', sa.String(), nullable=True, index=True),
        sa.Column('cover_art_url', sa.String(), nullable=True),
        sa.Column('audio_file_url', sa.String(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('release_date', sa.Date(), nullable=False),
        sa.Column('is_public', sa.Boolean(), default=True, nullable=False),
        sa.Column('play_count', sa.Integer(), default=0, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    # 購入テーブルの作成
    op.create_table(
        'purchase',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('user.id'), nullable=False, index=True),
        sa.Column('track_id', sa.String(), sa.ForeignKey('track.id'), nullable=False, index=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('purchase_date', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('payment_method', sa.Enum(PaymentMethodEnum), nullable=False),
        sa.Column('transaction_id', sa.String(), nullable=False, unique=True),
        sa.Column('status', sa.Enum(PurchaseStatusEnum), default=PurchaseStatusEnum.PENDING, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    # 再生履歴テーブルの作成
    op.create_table(
        'play_history',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('user.id'), nullable=True, index=True),
        sa.Column('track_id', sa.String(), sa.ForeignKey('track.id'), nullable=False, index=True),
        sa.Column('played_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('play_duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    # インデックスの作成
    op.create_index(op.f('ix_track_artist_id'), 'track', ['artist_id'], unique=False)
    op.create_index(op.f('ix_purchase_transaction_id'), 'purchase', ['transaction_id'], unique=True)
    op.create_index(op.f('ix_play_history_played_at'), 'play_history', ['played_at'], unique=False)


def downgrade():
    # テーブルの削除（逆順）
    op.drop_table('play_history')
    op.drop_table('purchase')
    op.drop_table('track')
    op.drop_table('user')
