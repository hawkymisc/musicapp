import stripe
import os
from fastapi import HTTPException
from typing import Dict, Any
import uuid

# Stripeの初期化
stripe.api_key = os.environ.get("STRIPE_API_KEY")


def process_payment(amount: float, payment_token: str, description: str) -> Dict[str, Any]:
    """
    Stripe決済を処理
    """
    try:
        # 金額を整数に変換（Stripeでは金額を最小通貨単位で指定）
        amount_in_cents = int(amount * 100)
        
        # 支払い処理
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="jpy",  # 日本円
            payment_method=payment_token,
            confirm=True,
            description=description
        )
        
        # 成功した場合の応答
        return {
            "success": True,
            "transaction_id": payment_intent.id,
            "amount": amount
        }
    
    except stripe.error.CardError as e:
        # カード決済エラー
        raise HTTPException(
            status_code=400,
            detail=f"カード決済に失敗しました: {e.user_message}"
        )
    
    except stripe.error.StripeError as e:
        # その他のStripeエラー
        raise HTTPException(
            status_code=500,
            detail=f"決済処理中にエラーが発生しました: {str(e)}"
        )
    
    except Exception as e:
        # 予期しないエラー
        raise HTTPException(
            status_code=500,
            detail=f"エラーが発生しました: {str(e)}"
        )
