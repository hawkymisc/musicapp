import React, { useState, useEffect } from 'react';
import paymentService from '../../services/payment';

const PurchaseButton = ({ track, userId, onPurchaseSuccess, className = '' }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [paymentFeatures, setPaymentFeatures] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 決済機能の状態を確認
    const checkFeatures = async () => {
      try {
        const features = await paymentService.checkPaymentFeatures();
        setPaymentFeatures(features);
      } catch (error) {
        console.error('Failed to check payment features:', error);
        setPaymentFeatures({ enabled: false, coming_soon_message: '決済機能の確認に失敗しました。' });
      }
    };

    checkFeatures();
  }, []);

  const handlePurchase = async () => {
    if (!paymentFeatures?.enabled) {
      setError(paymentFeatures?.coming_soon_message || '決済機能は現在利用できません。');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await paymentService.purchaseTrack(userId, track.id);
      onPurchaseSuccess && onPurchaseSuccess(result);
    } catch (error) {
      setError(error.message || '購入に失敗しました。');
    } finally {
      setIsLoading(false);
    }
  };

  // 決済機能が無効の場合
  if (paymentFeatures && !paymentFeatures.enabled) {
    return (
      <div className={`purchase-button-container ${className}`}>
        <button 
          disabled 
          className="purchase-button disabled"
          title={paymentFeatures.coming_soon_message}
        >
          決済準備中
        </button>
        <div className="coming-soon-message">
          {paymentFeatures.coming_soon_message}
        </div>
        <div className="free-download-note">
          現在は無料でダウンロードできます！
        </div>
      </div>
    );
  }

  // 決済機能が有効の場合
  return (
    <div className={`purchase-button-container ${className}`}>
      <button
        onClick={handlePurchase}
        disabled={isLoading || !paymentFeatures}
        className={`purchase-button ${isLoading ? 'loading' : ''}`}
      >
        {isLoading ? '処理中...' : `購入 ¥${track.price}`}
      </button>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <style jsx>{`
        .purchase-button-container {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .purchase-button {
          padding: 12px 24px;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .purchase-button:hover:not(:disabled) {
          background-color: #0056b3;
          transform: translateY(-1px);
        }
        
        .purchase-button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
          transform: none;
        }
        
        .purchase-button.loading {
          background-color: #6c757d;
        }
        
        .coming-soon-message {
          font-size: 14px;
          color: #6c757d;
          text-align: center;
          padding: 8px;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .free-download-note {
          font-size: 12px;
          color: #28a745;
          text-align: center;
          font-weight: 500;
        }
        
        .error-message {
          font-size: 14px;
          color: #dc3545;
          text-align: center;
          padding: 8px;
          background-color: #f8d7da;
          border: 1px solid #f5c6cb;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default PurchaseButton;