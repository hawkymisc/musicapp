// アプリケーション用ロガー

const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3
};

class Logger {
  constructor() {
    this.level = process.env.NODE_ENV === 'production' ? LOG_LEVELS.INFO : LOG_LEVELS.DEBUG;
  }

  setLevel(level) {
    this.level = level;
  }

  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logData = {
      timestamp,
      level,
      message,
      ...(data && { data }),
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    return logData;
  }

  error(message, data = null) {
    if (this.level >= LOG_LEVELS.ERROR) {
      const logData = this.formatMessage('ERROR', message, data);
      console.error('🔴', message, logData);
      
      // 本番環境では外部ログサービスに送信
      if (process.env.NODE_ENV === 'production') {
        this.sendToLogService(logData);
      }
    }
  }

  warn(message, data = null) {
    if (this.level >= LOG_LEVELS.WARN) {
      const logData = this.formatMessage('WARN', message, data);
      console.warn('🟡', message, logData);
    }
  }

  info(message, data = null) {
    if (this.level >= LOG_LEVELS.INFO) {
      const logData = this.formatMessage('INFO', message, data);
      console.info('🔵', message, logData);
    }
  }

  debug(message, data = null) {
    if (this.level >= LOG_LEVELS.DEBUG) {
      const logData = this.formatMessage('DEBUG', message, data);
      console.log('⚪', message, logData);
    }
  }

  // API エラー専用ログ
  apiError(endpoint, status, error, data = null) {
    this.error(`API Error: ${endpoint}`, {
      status,
      error: error.message || error,
      endpoint,
      ...data
    });
  }

  // ユーザーアクション追跡
  userAction(action, data = null) {
    this.info(`User Action: ${action}`, data);
  }

  // パフォーマンス追跡
  performance(metric, value, data = null) {
    this.info(`Performance: ${metric}`, {
      value,
      ...data
    });
  }

  // 外部ログサービスへの送信（本番環境用）
  sendToLogService(logData) {
    try {
      // 実際の実装では Sentry, LogRocket, DataDog などのサービスを使用
      fetch('/api/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(logData)
      }).catch(err => {
        console.error('Failed to send log to service:', err);
      });
    } catch (err) {
      console.error('Logger error:', err);
    }
  }
}

// シングルトンインスタンス
const logger = new Logger();

export default logger;
export { LOG_LEVELS };