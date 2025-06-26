import { describe, it, expect } from 'vitest';
import {
  validateEmail,
  validatePassword,
  validateDisplayName,
  validateTrackTitle,
  validatePrice,
  validateFileSize,
  sanitizeHtml,
  escapeHtml
} from '../validation';

describe('Validation Utils', () => {
  describe('validateEmail', () => {
    it('should validate correct email addresses', () => {
      expect(validateEmail('test@example.com')).toEqual({ isValid: true, message: '' });
      expect(validateEmail('user.name+tag@example.co.jp')).toEqual({ isValid: true, message: '' });
    });

    it('should reject invalid email addresses', () => {
      expect(validateEmail('')).toEqual({ isValid: false, message: 'メールアドレスを入力してください' });
      expect(validateEmail('invalid-email')).toEqual({ isValid: false, message: '有効なメールアドレスを入力してください' });
      expect(validateEmail('@example.com')).toEqual({ isValid: false, message: '有効なメールアドレスを入力してください' });
    });
  });

  describe('validatePassword', () => {
    it('should validate strong passwords', () => {
      expect(validatePassword('Password123')).toEqual({ isValid: true, message: '' });
      expect(validatePassword('MySecure1Pass')).toEqual({ isValid: true, message: '' });
    });

    it('should reject weak passwords', () => {
      expect(validatePassword('')).toEqual({ isValid: false, message: 'パスワードを入力してください' });
      expect(validatePassword('short')).toEqual({ isValid: false, message: 'パスワードは8文字以上で入力してください' });
      expect(validatePassword('12345678')).toEqual({ isValid: false, message: 'パスワードには英字を含めてください' });
      expect(validatePassword('onlyletters')).toEqual({ isValid: false, message: 'パスワードには数字を含めてください' });
    });
  });

  describe('validateDisplayName', () => {
    it('should validate proper display names', () => {
      expect(validateDisplayName('John')).toEqual({ isValid: true, message: '' });
      expect(validateDisplayName('田中太郎')).toEqual({ isValid: true, message: '' });
    });

    it('should reject invalid display names', () => {
      expect(validateDisplayName('')).toEqual({ isValid: false, message: '表示名を入力してください' });
      expect(validateDisplayName('A')).toEqual({ isValid: false, message: '表示名は2文字以上で入力してください' });
      expect(validateDisplayName('A'.repeat(51))).toEqual({ isValid: false, message: '表示名は50文字以下で入力してください' });
    });
  });

  describe('validateTrackTitle', () => {
    it('should validate proper track titles', () => {
      expect(validateTrackTitle('My Song')).toEqual({ isValid: true, message: '' });
      expect(validateTrackTitle('楽曲タイトル')).toEqual({ isValid: true, message: '' });
    });

    it('should reject invalid track titles', () => {
      expect(validateTrackTitle('')).toEqual({ isValid: false, message: 'タイトルを入力してください' });
      expect(validateTrackTitle('A'.repeat(101))).toEqual({ isValid: false, message: 'タイトルは100文字以下で入力してください' });
    });
  });

  describe('validatePrice', () => {
    it('should validate proper prices', () => {
      expect(validatePrice('100')).toEqual({ isValid: true, message: '' });
      expect(validatePrice('0')).toEqual({ isValid: true, message: '' });
      expect(validatePrice('9999.99')).toEqual({ isValid: true, message: '' });
    });

    it('should reject invalid prices', () => {
      expect(validatePrice('')).toEqual({ isValid: false, message: '価格を入力してください' });
      expect(validatePrice('invalid')).toEqual({ isValid: false, message: '価格を入力してください' });
      expect(validatePrice('-100')).toEqual({ isValid: false, message: '価格は0以上で入力してください' });
      expect(validatePrice('10001')).toEqual({ isValid: false, message: '価格は10,000円以下で入力してください' });
    });
  });

  describe('validateFileSize', () => {
    it('should validate files within size limit', () => {
      const mockFile = { size: 5 * 1024 * 1024 }; // 5MB
      expect(validateFileSize(mockFile, 10)).toEqual({ isValid: true, message: '' });
    });

    it('should reject files exceeding size limit', () => {
      const mockFile = { size: 15 * 1024 * 1024 }; // 15MB
      expect(validateFileSize(mockFile, 10)).toEqual({ 
        isValid: false, 
        message: 'ファイルサイズは10MB以下にしてください' 
      });
    });

    it('should reject missing files', () => {
      expect(validateFileSize(null, 10)).toEqual({ 
        isValid: false, 
        message: 'ファイルを選択してください' 
      });
    });
  });

  describe('sanitizeHtml', () => {
    it('should sanitize HTML content', () => {
      expect(sanitizeHtml('<script>alert("xss")</script>Hello')).toBe('&lt;script&gt;alert("xss")&lt;/script&gt;Hello');
      expect(sanitizeHtml('Normal text')).toBe('Normal text');
    });
  });

  describe('escapeHtml', () => {
    it('should escape HTML characters', () => {
      expect(escapeHtml('<div>Hello & Goodbye</div>')).toBe('&lt;div&gt;Hello &amp; Goodbye&lt;/div&gt;');
      expect(escapeHtml('"quoted" & \'single\'')).toBe('&quot;quoted&quot; &amp; &#39;single&#39;');
    });
  });
});