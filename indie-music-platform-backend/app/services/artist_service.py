def get_user_profile(db: Session, user_id: str) -> User:
    """
    ユーザープロフィールを取得
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
    return user


def get_artist_revenue(
    db: Session,
    artist_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    アーティスト収益情報を取得
    """
    # ユーザーがアーティストかチェック
    user = db.query(User).filter(User.id == artist_id).first()
    if not user or user.user_role != UserRole.ARTIST:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="アーティストが見つかりません"
        )
    
    # 日付範囲の設定
    if not start_date:
        start_date = datetime.now().date().replace(day=1)  # 今月の初日
    if not end_date:
        end_date = datetime.now().date()
    
    # 期間中の購入データの取得
    purchases = db.query(
        Purchase.purchase_date,
        Purchase.amount,
        Track.title
    ).join(
        Track, Purchase.track_id == Track.id
    ).filter(
        Track.artist_id == artist_id,
        Purchase.status == PurchaseStatus.COMPLETED,
        func.date(Purchase.purchase_date) >= start_date,
        func.date(Purchase.purchase_date) <= end_date
    ).all()
    
    # 日ごとの収益集計
    daily_revenue = {}
    total_revenue = 0
    
    for purchase in purchases:
        purchase_date = purchase.purchase_date.date().isoformat()
        amount = purchase.amount
        
        if purchase_date not in daily_revenue:
            daily_revenue[purchase_date] = 0
        
        daily_revenue[purchase_date] += amount
        total_revenue += amount
    
    # 楽曲ごとの収益集計
    track_revenue = db.query(
        Track.id,
        Track.title,
        func.count(Purchase.id).label("sales_count"),
        func.sum(Purchase.amount).label("total_amount")
    ).join(
        Purchase, Track.id == Purchase.track_id
    ).filter(
        Track.artist_id == artist_id,
        Purchase.status == PurchaseStatus.COMPLETED,
        func.date(Purchase.purchase_date) >= start_date,
        func.date(Purchase.purchase_date) <= end_date
    ).group_by(
        Track.id, Track.title
    ).order_by(
        desc("total_amount")
    ).all()
    
    # 手数料計算（例: 15%のプラットフォーム手数料）
    platform_fee = total_revenue * 0.15
    net_revenue = total_revenue - platform_fee
    
    # レスポンスの構築
    result = {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_revenue": total_revenue,
            "platform_fee": platform_fee,
            "net_revenue": net_revenue,
            "sales_count": len(purchases)
        },
        "daily_revenue": [
            {"date": date, "amount": amount}
            for date, amount in sorted(daily_revenue.items())
        ],
        "track_revenue": [
            {
                "track_id": str(item.id),
                "title": item.title,
                "sales_count": item.sales_count,
                "total_amount": float(item.total_amount) if item.total_amount else 0
            }
            for item in track_revenue
        ]
    }
    
    return result


def get_artist_stats(
    db: Session,
    artist_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    アーティスト統計情報を取得
    """
    # ユーザーがアーティストかチェック
    user = db.query(User).filter(User.id == artist_id).first()
    if not user or user.user_role != UserRole.ARTIST:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="アーティストが見つかりません"
        )
    
    # 日付範囲の設定
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()  # 過去30日
    if not end_date:
        end_date = datetime.now().date()
    
    # 全楽曲の合計再生回数
    total_plays = db.query(func.sum(Track.play_count)).filter(
        Track.artist_id == artist_id
    ).scalar() or 0
    
    # 期間中の再生数
    period_plays = db.query(func.count(PlayHistory.id)).join(
        Track, PlayHistory.track_id == Track.id
    ).filter(
        Track.artist_id == artist_id,
        func.date(PlayHistory.played_at) >= start_date,
        func.date(PlayHistory.played_at) <= end_date
    ).scalar() or 0
    
    # 楽曲ごとの再生数ランキング
    track_plays = db.query(
        Track.id,
        Track.title,
        func.count(PlayHistory.id).label("play_count")
    ).join(
        PlayHistory, Track.id == PlayHistory.track_id
    ).filter(
        Track.artist_id == artist_id,
        func.date(PlayHistory.played_at) >= start_date,
        func.date(PlayHistory.played_at) <= end_date
    ).group_by(
        Track.id, Track.title
    ).order_by(
        desc("play_count")
    ).limit(10).all()
    
    # 日ごとの再生数
    daily_plays = db.query(
        func.date(PlayHistory.played_at).label("play_date"),
        func.count(PlayHistory.id).label("play_count")
    ).join(
        Track, PlayHistory.track_id == Track.id
    ).filter(
        Track.artist_id == artist_id,
        func.date(PlayHistory.played_at) >= start_date,
        func.date(PlayHistory.played_at) <= end_date
    ).group_by(
        "play_date"
    ).order_by(
        "play_date"
    ).all()
    
    # レスポンスの構築
    result = {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_plays_all_time": total_plays,
            "total_plays_period": period_plays,
            "track_count": db.query(Track).filter(Track.artist_id == artist_id).count()
        },
        "top_tracks": [
            {
                "track_id": str(item.id),
                "title": item.title,
                "play_count": item.play_count
            }
            for item in track_plays
        ],
        "daily_plays": [
            {
                "date": item.play_date.isoformat(),
                "play_count": item.play_count
            }
            for item in daily_plays
        ]
    }
    
    return result


