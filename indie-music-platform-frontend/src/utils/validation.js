// バリデーション関数集

// メールアドレスの検証
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) return { isValid: false, message: 'メールアドレスを入力してください' };
  if (!emailRegex.test(email)) return { isValid: false, message: '有効なメールアドレスを入力してください' };
  return { isValid: true, message: '' };
};

// パスワードの検証
export const validatePassword = (password) => {
  if (!password) return { isValid: false, message: 'パスワードを入力してください' };
  if (password.length < 8) return { isValid: false, message: 'パスワードは8文字以上で入力してください' };
  if (!/[A-Za-z]/.test(password)) return { isValid: false, message: 'パスワードには英字を含めてください' };
  if (!/[0-9]/.test(password)) return { isValid: false, message: 'パスワードには数字を含めてください' };
  return { isValid: true, message: '' };
};

// 表示名の検証
export const validateDisplayName = (name) => {
  if (!name) return { isValid: false, message: '表示名を入力してください' };
  if (name.length < 2) return { isValid: false, message: '表示名は2文字以上で入力してください' };
  if (name.length > 50) return { isValid: false, message: '表示名は50文字以下で入力してください' };
  return { isValid: true, message: '' };
};

// 楽曲タイトルの検証
export const validateTrackTitle = (title) => {
  if (!title) return { isValid: false, message: 'タイトルを入力してください' };
  if (title.length < 1) return { isValid: false, message: 'タイトルを入力してください' };
  if (title.length > 100) return { isValid: false, message: 'タイトルは100文字以下で入力してください' };
  return { isValid: true, message: '' };
};

// 価格の検証
export const validatePrice = (price) => {
  const numPrice = parseFloat(price);
  if (!price || isNaN(numPrice)) return { isValid: false, message: '価格を入力してください' };
  if (numPrice < 0) return { isValid: false, message: '価格は0以上で入力してください' };
  if (numPrice > 10000) return { isValid: false, message: '価格は10,000円以下で入力してください' };
  return { isValid: true, message: '' };
};

// ファイルサイズの検証
export const validateFileSize = (file, maxSizeMB) => {
  if (!file) return { isValid: false, message: 'ファイルを選択してください' };
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  if (file.size > maxSizeBytes) {
    return { isValid: false, message: `ファイルサイズは${maxSizeMB}MB以下にしてください` };
  }
  return { isValid: true, message: '' };
};

// 音声ファイルの検証
export const validateAudioFile = (file) => {
  const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/m4a'];
  if (!file) return { isValid: false, message: 'ファイルを選択してください' };
  if (!allowedTypes.includes(file.type)) {
    return { isValid: false, message: '対応している音声ファイル形式を選択してください（MP3, WAV, FLAC, M4A）' };
  }
  return validateFileSize(file, 50);
};

// 画像ファイルの検証
export const validateImageFile = (file) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  if (!file) return { isValid: false, message: 'ファイルを選択してください' };
  if (!allowedTypes.includes(file.type)) {
    return { isValid: false, message: '対応している画像ファイル形式を選択してください（JPEG, PNG, GIF, WebP）' };
  }
  return validateFileSize(file, 5);
};

// HTMLサニタイズ
export const sanitizeHtml = (str) => {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
};

// XSS対策のための文字列エスケープ
export const escapeHtml = (text) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
};