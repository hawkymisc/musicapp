import pytest
from fastapi import status
from unittest.mock import patch


# 支払い処理のモック
@pytest.fixture
def mock_process_payment(monkeypatch):
    def mock_process(*args, **kwargs):
        return {
            "success": True,
            "transaction_id": "test_transaction_1234",
            "amount": 500
        }
    
    # Stripe PaymentIntent.create をモック
    def mock_payment_intent_create(*args, **kwargs):
        class MockPaymentIntent:
            id = "test_transaction_1234"
        return MockPaymentIntent()
    
    import stripe
    monkeypatch.setattr(stripe.PaymentIntent, "create", mock_payment_intent_create)


def test_purchase_track(client, db, test_track, test_listener, mock_firebase_auth, mock_process_payment):
    """
    楽曲購入テスト
    """
    purchase_data = {
        "track_id": test_track.id,
        "amount": 500,
        "payment_method": "CREDIT_CARD",
        "payment_token": "test_payment_token"
    }
    
    # リスナーとして認証
    headers = {"Authorization": f"Bearer listener_token"}
    
    response = client.post(
        "/api/v1/purchases/",
        headers=headers,
        json=purchase_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["track_id"] == test_track.id
    assert data["user_id"] == test_listener.id
    assert data["amount"] == purchase_data["amount"]
    assert data["status"] == "completed"


def test_get_user_purchases(client, db, test_track, test_listener, mock_firebase_auth, mock_process_payment):
    """
    ユーザーの購入履歴取得テスト
    """
    # 先に購入を実行
    purchase_data = {
        "track_id": test_track.id,
        "amount": 500,
        "payment_method": "CREDIT_CARD",
        "payment_token": "test_payment_token"
    }
    
    headers = {"Authorization": f"Bearer listener_token"}
    
    client.post(
        "/api/v1/purchases/",
        headers=headers,
        json=purchase_data
    )
    
    # 購入履歴を取得
    response = client.get(
        "/api/v1/purchases/",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) >= 1
    assert data[0]["track_id"] == test_track.id
    assert data[0]["user_id"] == test_listener.id


