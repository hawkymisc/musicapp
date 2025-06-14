import React, { useState, useEffect } from 'react';
import paymentService from '../../services/payment';

const DownloadButton = ({ track, userId, className = '' }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [paymentFeatures, setPaymentFeatures] = useState(null);
  const [error, setError] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);

  useEffect(() => {
    // 決済機能の状態を確認
    const checkFeatures = async () => {
      try {
        const features = await paymentService.checkPaymentFeatures();
        setPaymentFeatures(features);
      } catch (error) {
        console.error('Failed to check payment features:', error);
        setPaymentFeatures({ enabled: false, downloads_enabled: true });
      }
    };

    checkFeatures();
  }, []);

  const handleDownload = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // 決済機能が無効の場合は無料ダウンロード
      const endpoint = `/purchases/track/${track.id}/download`;
      const response = await fetch(`/api/v1${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${userId}`,
        },
      });

      if (!response.ok) {
        throw new Error('ダウンロードに失敗しました。');
      }

      const data = await response.json();
      
      // ダウンロードURLを開く
      const link = document.createElement('a');
      link.href = data.download_url;
      link.download = `${track.title}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setDownloadUrl(data.download_url);
    } catch (error) {
      setError(error.message || 'ダウンロードに失敗しました。');
    } finally {
      setIsLoading(false);
    }
  };

  // ダウンロード機能が無効の場合
  if (paymentFeatures && !paymentFeatures.downloads_enabled) {
    return (
      <div className={`download-button-container ${className}`}>
        <button disabled className="download-button disabled">
          ダウンロード準備中
        </button>
        <div className="info-message">
          ダウンロード機能は近日公開予定です。
        </div>
      </div>
    );
  }

  return (
    <div className={`download-button-container ${className}`}>
      <button
        onClick={handleDownload}
        disabled={isLoading || !paymentFeatures}
        className={`download-button ${isLoading ? 'loading' : ''}`}
      >
        {isLoading ? 'ダウンロード中...' : 'ダウンロード'}
      </button>
      
      {!paymentFeatures?.enabled && (
        <div className="free-download-message">
          🎉 現在は無料ダウンロード期間中です！
        </div>
      )}
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <style jsx>{`
        .download-button-container {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .download-button {
          padding: 10px 20px;
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .download-button:hover:not(:disabled) {
          background-color: #218838;
          transform: translateY(-1px);
        }
        
        .download-button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
          transform: none;
        }
        
        .download-button.loading {
          background-color: #6c757d;
        }
        
        .free-download-message {
          font-size: 12px;
          color: #28a745;
          text-align: center;
          font-weight: 500;
          padding: 4px 8px;
          background-color: #d4edda;
          border: 1px solid #c3e6cb;
          border-radius: 4px;
        }
        
        .info-message {
          font-size: 12px;
          color: #6c757d;
          text-align: center;
          padding: 4px 8px;
          background-color: #f8f9fa;
          border-radius: 4px;
        }
        
        .error-message {
          font-size: 12px;
          color: #dc3545;
          text-align: center;
          padding: 4px 8px;
          background-color: #f8d7da;
          border: 1px solid #f5c6cb;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
};

export default DownloadButton;