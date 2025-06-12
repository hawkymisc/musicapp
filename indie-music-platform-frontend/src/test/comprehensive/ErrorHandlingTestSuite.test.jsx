/**
 * フロントエンド包括的エラーハンドリングテストスイート
 * 
 * 異常系・エラーケース・ネットワーク障害・ユーザー操作エラーを
 * 網羅的にテストします。
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'

// Mock API responses
const mockAPI = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn()
}

vi.mock('../../services/api.js', () => ({
  default: mockAPI
}))

// Test utilities
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

const renderWithProviders = (component, mockContextValues = {}) => {
  const defaultAuthContext = {
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
    loading: false,
    error: null,
    ...mockContextValues.auth
  }
  
  const defaultPlayerContext = {
    currentTrack: null,
    isPlaying: false,
    play: vi.fn(),
    pause: vi.fn(),
    setVolume: vi.fn(),
    error: null,
    ...mockContextValues.player
  }

  return render(
    <BrowserRouter>
      <AuthContext.Provider value={defaultAuthContext}>
        <PlayerContext.Provider value={defaultPlayerContext}>
          {component}
        </PlayerContext.Provider>
      </AuthContext.Provider>
    </BrowserRouter>
  )
}

describe('包括的エラーハンドリングテストスイート', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // コンソールエラーを一時的に無効化（テスト中の意図的エラー用）
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ==================== ネットワークエラーテスト ====================
  
  describe('ネットワークエラーハンドリング', () => {
    it('API接続失敗時のエラー表示', async () => {
      // TrackListコンポーネントでのネットワークエラー
      const TrackList = require('../../components/track/TrackList.jsx').default
      
      // ネットワークエラーをシミュレート
      mockAPI.get.mockRejectedValue(new Error('Network Error'))
      
      renderWithRouter(<TrackList />)
      
      await waitFor(() => {
        expect(screen.getByText(/ネットワークエラーが発生しました/)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /再試行/ })).toBeInTheDocument()
      })
    })

    it('タイムアウトエラーの処理', async () => {
      const SearchResults = require('../../components/search/SearchResults.jsx').default
      
      // タイムアウトエラーをシミュレート
      const timeoutError = new Error('Request timeout')
      timeoutError.code = 'TIMEOUT'
      mockAPI.get.mockRejectedValue(timeoutError)
      
      renderWithRouter(<SearchResults query="test" />)
      
      await waitFor(() => {
        expect(screen.getByText(/リクエストがタイムアウトしました/)).toBeInTheDocument()
        expect(screen.getByText(/接続が遅い可能性があります/)).toBeInTheDocument()
      })
    })

    it('DNS解決エラーの処理', async () => {
      const ArtistProfile = require('../../components/artist/ArtistProfile.jsx').default
      
      // DNS解決エラーをシミュレート
      const dnsError = new Error('getaddrinfo ENOTFOUND')
      dnsError.code = 'ENOTFOUND'
      mockAPI.get.mockRejectedValue(dnsError)
      
      renderWithRouter(<ArtistProfile artistId="test-id" />)
      
      await waitFor(() => {
        expect(screen.getByText(/サーバーに接続できません/)).toBeInTheDocument()
        expect(screen.getByText(/インターネット接続を確認してください/)).toBeInTheDocument()
      })
    })

    it('SSL証明書エラーの処理', async () => {
      const LoginForm = require('../../components/auth/LoginForm.jsx').default
      
      // SSL証明書エラーをシミュレート
      const sslError = new Error('certificate has expired')
      sslError.code = 'CERT_HAS_EXPIRED'
      mockAPI.post.mockRejectedValue(sslError)
      
      renderWithProviders(<LoginForm />)
      
      const emailInput = screen.getByLabelText('メールアドレス')
      const passwordInput = screen.getByLabelText('パスワード')
      const submitButton = screen.getByRole('button', { name: 'ログイン' })
      
      await userEvent.type(emailInput, 'test@example.com')
      await userEvent.type(passwordInput, 'password123')
      await userEvent.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/セキュリティ証明書に問題があります/)).toBeInTheDocument()
        expect(screen.getByText(/管理者にお問い合わせください/)).toBeInTheDocument()
      })
    })
  })

  // ==================== HTTPステータスエラーテスト ====================
  
  describe('HTTPステータスエラーハンドリング', () => {
    it('401 Unauthorized エラーの処理', async () => {
      const TrackDetail = require('../../components/track/TrackDetail.jsx').default
      
      const unauthorizedError = new Error('Unauthorized')
      unauthorizedError.response = { status: 401, data: { detail: 'Token expired' } }
      mockAPI.get.mockRejectedValue(unauthorizedError)
      
      renderWithProviders(<TrackDetail trackId="test-id" />)
      
      await waitFor(() => {
        expect(screen.getByText(/ログインが必要です/)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /ログインページへ/ })).toBeInTheDocument()
      })
    })

    it('403 Forbidden エラーの処理', async () => {
      const TrackUpload = require('../../components/track/TrackUpload.jsx').default
      
      const forbiddenError = new Error('Forbidden')
      forbiddenError.response = { status: 403, data: { detail: 'Access denied' } }
      mockAPI.post.mockRejectedValue(forbiddenError)
      
      renderWithProviders(<TrackUpload />)
      
      const titleInput = screen.getByLabelText('楽曲タイトル')
      const submitButton = screen.getByRole('button', { name: 'アップロード' })
      
      await userEvent.type(titleInput, 'Test Track')
      await userEvent.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/この操作を実行する権限がありません/)).toBeInTheDocument()
        expect(screen.getByText(/アカウントの種類を確認してください/)).toBeInTheDocument()
      })
    })

    it('404 Not Found エラーの処理', async () => {
      const UserProfile = require('../../components/user/UserProfile.jsx').default
      
      const notFoundError = new Error('Not Found')
      notFoundError.response = { status: 404, data: { detail: 'User not found' } }
      mockAPI.get.mockRejectedValue(notFoundError)
      
      renderWithRouter(<UserProfile userId="nonexistent-id" />)
      
      await waitFor(() => {
        expect(screen.getByText(/ユーザーが見つかりません/)).toBeInTheDocument()
        expect(screen.getByText(/URLを確認してください/)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /ホームに戻る/ })).toBeInTheDocument()
      })
    })

    it('429 Too Many Requests エラーの処理', async () => {
      const SearchBar = require('../../components/search/SearchBar.jsx').default
      
      const rateLimitError = new Error('Too Many Requests')
      rateLimitError.response = { 
        status: 429, 
        data: { detail: 'Rate limit exceeded' },
        headers: { 'retry-after': '60' }
      }
      mockAPI.get.mockRejectedValue(rateLimitError)
      
      const mockOnSearch = vi.fn()
      renderWithRouter(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByPlaceholderText('楽曲、アーティストを検索...')
      await userEvent.type(searchInput, 'test{enter}')
      
      await waitFor(() => {
        expect(screen.getByText(/リクエストが多すぎます/)).toBeInTheDocument()
        expect(screen.getByText(/60秒後に再試行してください/)).toBeInTheDocument()
      })
    })

    it('500 Internal Server Error の処理', async () => {
      const PurchaseButton = require('../../components/purchase/PurchaseButton.jsx').default
      
      const serverError = new Error('Internal Server Error')
      serverError.response = { status: 500, data: { detail: 'Database error' } }
      mockAPI.post.mockRejectedValue(serverError)
      
      const mockTrack = { id: 'track-1', title: 'Test Track', price: 300 }
      renderWithRouter(<PurchaseButton track={mockTrack} />)
      
      const purchaseButton = screen.getByRole('button', { name: /購入/ })
      await userEvent.click(purchaseButton)
      
      const confirmButton = screen.getByRole('button', { name: '購入確定' })
      await userEvent.click(confirmButton)
      
      await waitFor(() => {
        expect(screen.getByText(/サーバーでエラーが発生しました/)).toBeInTheDocument()
        expect(screen.getByText(/しばらく時間をおいて再試行してください/)).toBeInTheDocument()
      })
    })

    it('503 Service Unavailable の処理', async () => {
      const AudioPlayer = require('../../components/player/AudioPlayer.jsx').default
      
      const serviceUnavailableError = new Error('Service Unavailable')
      serviceUnavailableError.response = { 
        status: 503, 
        data: { detail: 'Service temporarily unavailable' }
      }
      mockAPI.get.mockRejectedValue(serviceUnavailableError)
      
      const mockTrack = { id: 'track-1', title: 'Test Track', audio_file_url: 'test.mp3' }
      renderWithProviders(<AudioPlayer />, {
        player: { currentTrack: mockTrack }
      })
      
      await waitFor(() => {
        expect(screen.getByText(/サービスが一時的に利用できません/)).toBeInTheDocument()
        expect(screen.getByText(/メンテナンス中の可能性があります/)).toBeInTheDocument()
      })
    })
  })

  // ==================== フォームバリデーションエラーテスト ====================
  
  describe('フォームバリデーションエラーハンドリング', () => {
    it('必須フィールド未入力エラー', async () => {
      const RegisterForm = require('../../components/auth/RegisterForm.jsx').default
      
      renderWithRouter(<RegisterForm />)
      
      const submitButton = screen.getByRole('button', { name: '登録' })
      await userEvent.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText('表示名は必須です')).toBeInTheDocument()
        expect(screen.getByText('メールアドレスは必須です')).toBeInTheDocument()
        expect(screen.getByText('パスワードは必須です')).toBeInTheDocument()
      })
    })

    it('メールアドレス形式エラー', async () => {
      const RegisterForm = require('../../components/auth/RegisterForm.jsx').default
      
      renderWithRouter(<RegisterForm />)
      
      const emailInput = screen.getByLabelText('メールアドレス')
      await userEvent.type(emailInput, 'invalid-email')
      
      // フィールドからフォーカスを外してバリデーションを発動
      fireEvent.blur(emailInput)
      
      await waitFor(() => {
        expect(screen.getByText('正しいメールアドレスを入力してください')).toBeInTheDocument()
      })
    })

    it('パスワード強度エラー', async () => {
      const RegisterForm = require('../../components/auth/RegisterForm.jsx').default
      
      renderWithRouter(<RegisterForm />)
      
      const passwordInput = screen.getByLabelText('パスワード', { exact: true })
      await userEvent.type(passwordInput, '123')
      
      fireEvent.blur(passwordInput)
      
      await waitFor(() => {
        expect(screen.getByText('パスワードは8文字以上である必要があります')).toBeInTheDocument()
      })
    })

    it('パスワード確認不一致エラー', async () => {
      const RegisterForm = require('../../components/auth/RegisterForm.jsx').default
      
      renderWithRouter(<RegisterForm />)
      
      const passwordInput = screen.getByLabelText('パスワード', { exact: true })
      const confirmPasswordInput = screen.getByLabelText('パスワード確認')
      
      await userEvent.type(passwordInput, 'password123')
      await userEvent.type(confirmPasswordInput, 'password456')
      
      fireEvent.blur(confirmPasswordInput)
      
      await waitFor(() => {
        expect(screen.getByText('パスワードが一致しません')).toBeInTheDocument()
      })
    })

    it('数値範囲外エラー', async () => {
      const TrackUpload = require('../../components/track/TrackUpload.jsx').default
      
      renderWithRouter(<TrackUpload />)
      
      const priceInput = screen.getByLabelText('価格')
      await userEvent.clear(priceInput)
      await userEvent.type(priceInput, '99999')
      
      fireEvent.blur(priceInput)
      
      await waitFor(() => {
        expect(screen.getByText('価格は0円から9999円の間で設定してください')).toBeInTheDocument()
      })
    })

    it('ファイルサイズ超過エラー', async () => {
      const TrackUpload = require('../../components/track/TrackUpload.jsx').default
      
      renderWithRouter(<TrackUpload />)
      
      // 大きなファイルを模擬
      const largeFile = new File(['x'.repeat(50 * 1024 * 1024)], 'large.mp3', { 
        type: 'audio/mpeg' 
      })
      
      const fileInput = screen.getByLabelText('音声ファイル')
      await userEvent.upload(fileInput, largeFile)
      
      await waitFor(() => {
        expect(screen.getByText('ファイルサイズは10MB以下にしてください')).toBeInTheDocument()
      })
    })

    it('不正なファイル形式エラー', async () => {
      const TrackUpload = require('../../components/track/TrackUpload.jsx').default
      
      renderWithRouter(<TrackUpload />)
      
      // 不正なファイル形式を模擬
      const invalidFile = new File(['test'], 'document.pdf', { 
        type: 'application/pdf' 
      })
      
      const fileInput = screen.getByLabelText('音声ファイル')
      await userEvent.upload(fileInput, invalidFile)
      
      await waitFor(() => {
        expect(screen.getByText('音声ファイル（MP3, WAV, FLAC）のみアップロード可能です')).toBeInTheDocument()
      })
    })
  })

  // ==================== 音声再生エラーテスト ====================
  
  describe('音声再生エラーハンドリング', () => {
    it('音声ファイル読み込みエラー', async () => {
      const AudioPlayer = require('../../components/player/AudioPlayer.jsx').default
      
      const mockTrack = { 
        id: 'track-1', 
        title: 'Error Track', 
        audio_file_url: 'https://invalid-url.com/nonexistent.mp3' 
      }
      
      renderWithProviders(<AudioPlayer />, {
        player: { currentTrack: mockTrack, error: 'ファイルの読み込みに失敗しました' }
      })
      
      expect(screen.getByText('ファイルの読み込みに失敗しました')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /再試行/ })).toBeInTheDocument()
    })

    it('音声形式サポートエラー', async () => {
      const AudioPlayer = require('../../components/player/AudioPlayer.jsx').default
      
      const mockTrack = { 
        id: 'track-1', 
        title: 'Unsupported Track', 
        audio_file_url: 'https://example.com/track.ogg' 
      }
      
      renderWithProviders(<AudioPlayer />, {
        player: { 
          currentTrack: mockTrack, 
          error: 'この音声形式はサポートされていません' 
        }
      })
      
      expect(screen.getByText('この音声形式はサポートされていません')).toBeInTheDocument()
      expect(screen.getByText('ブラウザを更新してください')).toBeInTheDocument()
    })

    it('DRM保護コンテンツエラー', async () => {
      const AudioPlayer = require('../../components/player/AudioPlayer.jsx').default
      
      const mockTrack = { 
        id: 'track-1', 
        title: 'DRM Track', 
        audio_file_url: 'https://example.com/drm-track.mp3' 
      }
      
      renderWithProviders(<AudioPlayer />, {
        player: { 
          currentTrack: mockTrack, 
          error: 'この楽曲は保護されているため再生できません' 
        }
      })
      
      expect(screen.getByText('この楽曲は保護されているため再生できません')).toBeInTheDocument()
      expect(screen.getByText('別のブラウザで試してください')).toBeInTheDocument()
    })
  })

  // ==================== 決済エラーテスト ====================
  
  describe('決済エラーハンドリング', () => {
    it('クレジットカード決済エラー', async () => {
      const PurchaseButton = require('../../components/purchase/PurchaseButton.jsx').default
      
      const paymentError = new Error('Payment failed')
      paymentError.response = { 
        status: 400, 
        data: { detail: 'カードが拒否されました' } 
      }
      mockAPI.post.mockRejectedValue(paymentError)
      
      const mockTrack = { id: 'track-1', title: 'Test Track', price: 300 }
      renderWithRouter(<PurchaseButton track={mockTrack} />)
      
      const purchaseButton = screen.getByRole('button', { name: /購入/ })
      await userEvent.click(purchaseButton)
      
      const confirmButton = screen.getByRole('button', { name: '購入確定' })
      await userEvent.click(confirmButton)
      
      await waitFor(() => {
        expect(screen.getByText('カードが拒否されました')).toBeInTheDocument()
        expect(screen.getByText('別のカードを試すか、カード会社にお問い合わせください')).toBeInTheDocument()
      })
    })

    it('残高不足エラー', async () => {
      const PurchaseButton = require('../../components/purchase/PurchaseButton.jsx').default
      
      const insufficientFundsError = new Error('Insufficient funds')
      insufficientFundsError.response = { 
        status: 400, 
        data: { detail: '残高が不足しています' } 
      }
      mockAPI.post.mockRejectedValue(insufficientFundsError)
      
      const mockTrack = { id: 'track-1', title: 'Expensive Track', price: 10000 }
      renderWithRouter(<PurchaseButton track={mockTrack} />)
      
      const purchaseButton = screen.getByRole('button', { name: /購入/ })
      await userEvent.click(purchaseButton)
      
      const confirmButton = screen.getByRole('button', { name: '購入確定' })
      await userEvent.click(confirmButton)
      
      await waitFor(() => {
        expect(screen.getByText('残高が不足しています')).toBeInTheDocument()
        expect(screen.getByText('チャージしてから再試行してください')).toBeInTheDocument()
      })
    })

    it('重複購入エラー', async () => {
      const PurchaseButton = require('../../components/purchase/PurchaseButton.jsx').default
      
      const duplicateError = new Error('Already purchased')
      duplicateError.response = { 
        status: 400, 
        data: { detail: 'この楽曲は既に購入済みです' } 
      }
      mockAPI.post.mockRejectedValue(duplicateError)
      
      const mockTrack = { id: 'track-1', title: 'Owned Track', price: 300 }
      renderWithRouter(<PurchaseButton track={mockTrack} />)
      
      const purchaseButton = screen.getByRole('button', { name: /購入/ })
      await userEvent.click(purchaseButton)
      
      const confirmButton = screen.getByRole('button', { name: '購入確定' })
      await userEvent.click(confirmButton)
      
      await waitFor(() => {
        expect(screen.getByText('この楽曲は既に購入済みです')).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /ライブラリで確認/ })).toBeInTheDocument()
      })
    })
  })

  // ==================== ブラウザ互換性エラーテスト ====================
  
  describe('ブラウザ互換性エラーハンドリング', () => {
    it('LocalStorage利用不可エラー', async () => {
      // LocalStorageを無効化
      const originalLocalStorage = window.localStorage
      Object.defineProperty(window, 'localStorage', {
        value: null,
        writable: true
      })
      
      const LoginForm = require('../../components/auth/LoginForm.jsx').default
      
      renderWithProviders(<LoginForm />)
      
      await waitFor(() => {
        expect(screen.getByText(/ブラウザの設定でローカルストレージが無効になっています/)).toBeInTheDocument()
        expect(screen.getByText(/プライベートモードを解除してください/)).toBeInTheDocument()
      })
      
      // 元に戻す
      window.localStorage = originalLocalStorage
    })

    it('古いブラウザでのFileReader不対応', async () => {
      // FileReaderを無効化
      const originalFileReader = window.FileReader
      window.FileReader = undefined
      
      const TrackUpload = require('../../components/track/TrackUpload.jsx').default
      
      renderWithRouter(<TrackUpload />)
      
      await waitFor(() => {
        expect(screen.getByText(/お使いのブラウザはファイルアップロードに対応していません/)).toBeInTheDocument()
        expect(screen.getByText(/ブラウザを最新版に更新してください/)).toBeInTheDocument()
      })
      
      // 元に戻す
      window.FileReader = originalFileReader
    })

    it('WebAudio API不対応エラー', async () => {
      // AudioContextを無効化
      const originalAudioContext = window.AudioContext || window.webkitAudioContext
      window.AudioContext = undefined
      window.webkitAudioContext = undefined
      
      const AudioVisualizer = require('../../components/player/AudioVisualizer.jsx').default
      
      renderWithRouter(<AudioVisualizer />)
      
      await waitFor(() => {
        expect(screen.getByText(/音声の可視化機能は利用できません/)).toBeInTheDocument()
        expect(screen.getByText(/最新のブラウザをご利用ください/)).toBeInTheDocument()
      })
      
      // 元に戻す
      window.AudioContext = originalAudioContext
      window.webkitAudioContext = originalAudioContext
    })
  })

  // ==================== メモリ・パフォーマンスエラーテスト ====================
  
  describe('メモリ・パフォーマンスエラーハンドリング', () => {
    it('メモリ不足による画像読み込み失敗', async () => {
      const TrackCard = require('../../components/track/TrackCard.jsx').default
      
      const mockTrack = {
        id: 'track-1',
        title: 'Memory Test Track',
        cover_art_url: 'https://example.com/very-large-image.jpg',
        artist_name: 'Test Artist',
        price: 300
      }
      
      renderWithRouter(<TrackCard track={mockTrack} />)
      
      // 画像読み込みエラーをシミュレート
      const images = screen.getAllByRole('img')
      if (images.length > 0) {
        fireEvent.error(images[0])
        
        await waitFor(() => {
          expect(screen.getByText(/画像の読み込みに失敗しました/)).toBeInTheDocument()
        })
      }
    })

    it('大量データ表示時のパフォーマンス警告', async () => {
      const TrackList = require('../../components/track/TrackList.jsx').default
      
      // 大量のトラックデータを模擬
      const largeTracks = Array.from({ length: 10000 }, (_, i) => ({
        id: `track-${i}`,
        title: `Track ${i}`,
        artist_name: `Artist ${i}`,
        price: 300
      }))
      
      mockAPI.get.mockResolvedValue({ data: largeTracks })
      
      renderWithRouter(<TrackList />)
      
      await waitFor(() => {
        expect(screen.getByText(/大量のデータを表示しています/)).toBeInTheDocument()
        expect(screen.getByText(/パフォーマンスが低下する可能性があります/)).toBeInTheDocument()
      })
    })
  })

  // ==================== セッション・認証エラーテスト ====================
  
  describe('セッション・認証エラーハンドリング', () => {
    it('セッション期限切れエラー', async () => {
      const ProtectedComponent = require('../../components/common/ProtectedRoute.jsx').default
      
      const sessionExpiredError = new Error('Session expired')
      sessionExpiredError.response = { status: 401, data: { detail: 'Session expired' } }
      
      renderWithProviders(<ProtectedComponent />, {
        auth: { 
          user: null, 
          error: 'セッションの有効期限が切れました' 
        }
      })
      
      expect(screen.getByText('セッションの有効期限が切れました')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /再ログイン/ })).toBeInTheDocument()
    })

    it('同時ログイン制限エラー', async () => {
      const LoginForm = require('../../components/auth/LoginForm.jsx').default
      
      const concurrentLoginError = new Error('Concurrent login detected')
      concurrentLoginError.response = { 
        status: 409, 
        data: { detail: '他のデバイスでログインが検出されました' } 
      }
      mockAPI.post.mockRejectedValue(concurrentLoginError)
      
      renderWithProviders(<LoginForm />)
      
      const emailInput = screen.getByLabelText('メールアドレス')
      const passwordInput = screen.getByLabelText('パスワード')
      const submitButton = screen.getByRole('button', { name: 'ログイン' })
      
      await userEvent.type(emailInput, 'test@example.com')
      await userEvent.type(passwordInput, 'password123')
      await userEvent.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText('他のデバイスでログインが検出されました')).toBeInTheDocument()
        expect(screen.getByText('続行しますか？')).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /強制ログイン/ })).toBeInTheDocument()
      })
    })
  })

  // ==================== 復旧・リトライメカニズムテスト ====================
  
  describe('エラー復旧・リトライメカニズム', () => {
    it('自動リトライ機能', async () => {
      const TrackList = require('../../components/track/TrackList.jsx').default
      
      // 最初は失敗、2回目は成功
      mockAPI.get
        .mockRejectedValueOnce(new Error('Network Error'))
        .mockResolvedValueOnce({ data: [] })
      
      renderWithRouter(<TrackList />)
      
      // 最初のエラー表示
      await waitFor(() => {
        expect(screen.getByText(/ネットワークエラーが発生しました/)).toBeInTheDocument()
      })
      
      // 自動リトライ後の成功
      await waitFor(() => {
        expect(screen.queryByText(/ネットワークエラーが発生しました/)).not.toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('手動リトライボタン', async () => {
      const SearchResults = require('../../components/search/SearchResults.jsx').default
      
      mockAPI.get.mockRejectedValue(new Error('API Error'))
      
      renderWithRouter(<SearchResults query="test" />)
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /再試行/ })).toBeInTheDocument()
      })
      
      // 成功するように設定
      mockAPI.get.mockResolvedValue({ data: [] })
      
      const retryButton = screen.getByRole('button', { name: /再試行/ })
      await userEvent.click(retryButton)
      
      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /再試行/ })).not.toBeInTheDocument()
      })
    })

    it('オフライン状態検出と復旧', async () => {
      const NetworkStatus = require('../../components/common/NetworkStatus.jsx').default
      
      renderWithRouter(<NetworkStatus />)
      
      // オフライン状態をシミュレート
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false
      })
      
      fireEvent(window, new Event('offline'))
      
      await waitFor(() => {
        expect(screen.getByText(/インターネット接続がありません/)).toBeInTheDocument()
        expect(screen.getByText(/オフラインモードで動作しています/)).toBeInTheDocument()
      })
      
      // オンライン復旧をシミュレート
      Object.defineProperty(navigator, 'onLine', {
        value: true
      })
      
      fireEvent(window, new Event('online'))
      
      await waitFor(() => {
        expect(screen.getByText(/インターネット接続が復旧しました/)).toBeInTheDocument()
      })
    })
  })
})