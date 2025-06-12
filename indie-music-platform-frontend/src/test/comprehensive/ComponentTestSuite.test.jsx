/**
 * フロントエンド包括的コンポーネントテストスイート
 * 
 * Seedデータと連携して、すべてのコンポーネントの機能を
 * 網羅的にテストします。
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'

// モックデータ（Seedデータに基づく）
const mockSeedData = {
  tracks: [
    {
      id: "track-1",
      title: "青い空の下で",
      artist_name: "青空バンド",
      artist_id: "artist-1",
      genre: "ポップ",
      duration: 245,
      price: 300,
      play_count: 150,
      cover_art_url: "https://example.com/covers/blue_sky.jpg"
    },
    {
      id: "track-2", 
      title: "Digital Dreams",
      artist_name: "夜想曲",
      artist_id: "artist-2",
      genre: "エレクトロニック",
      duration: 320,
      price: 400,
      play_count: 89,
      cover_art_url: "https://example.com/covers/digital_dreams.jpg"
    }
  ],
  artists: [
    {
      id: "artist-1",
      display_name: "青空バンド",
      user_role: "ARTIST",
      track_count: 2
    },
    {
      id: "artist-2",
      display_name: "夜想曲", 
      user_role: "ARTIST",
      track_count: 2
    }
  ],
  user: {
    id: "user-1",
    email: "test@example.com",
    display_name: "テストユーザー",
    user_role: "LISTENER"
  }
}

// テストユーティリティ
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

const renderWithProviders = (component, mockContextValues = {}) => {
  const defaultAuthContext = {
    user: mockSeedData.user,
    login: vi.fn(),
    logout: vi.fn(),
    loading: false,
    ...mockContextValues.auth
  }
  
  const defaultPlayerContext = {
    currentTrack: null,
    isPlaying: false,
    play: vi.fn(),
    pause: vi.fn(),
    setVolume: vi.fn(),
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

// API モック
const mockAPI = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn()
}

vi.mock('../../services/api.js', () => ({
  default: mockAPI
}))

describe('包括的コンポーネントテストスイート', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // デフォルトのAPIレスポンス設定
    mockAPI.get.mockResolvedValue({ data: mockSeedData.tracks })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // ==================== レイアウトコンポーネントテスト ====================
  
  describe('Header コンポーネント', () => {
    it('ログイン済みユーザーの情報を表示する', () => {
      const Header = require('../../components/layout/Header.jsx').default
      renderWithProviders(<Header />)
      
      expect(screen.getByText('INDIE MUSIC')).toBeInTheDocument()
      expect(screen.getByText('ホーム')).toBeInTheDocument()
      expect(screen.getByText('検索')).toBeInTheDocument()
      expect(screen.getByText('マイライブラリ')).toBeInTheDocument()
      
      // ユーザーアバターの初期文字
      expect(screen.getByText('テ')).toBeInTheDocument()
    })

    it('アーティストユーザーにはアーティストバッジが表示される', () => {
      const Header = require('../../components/layout/Header.jsx').default
      const artistUser = { ...mockSeedData.user, user_role: 'ARTIST' }
      
      renderWithProviders(<Header />, {
        auth: { user: artistUser }
      })
      
      expect(screen.getByText('ARTIST')).toBeInTheDocument()
      expect(screen.getByText('アーティストパネル')).toBeInTheDocument()
    })

    it('ナビゲーションリンクが機能する', async () => {
      const Header = require('../../components/layout/Header.jsx').default
      renderWithProviders(<Header />)
      
      const homeLink = screen.getByText('ホーム')
      const searchLink = screen.getByText('検索')
      
      expect(homeLink).toHaveAttribute('href', '/')
      expect(searchLink).toHaveAttribute('href', '/search')
    })
  })

  // ==================== 楽曲関連コンポーネントテスト ====================
  
  describe('TrackList コンポーネント', () => {
    it('楽曲一覧を正しく表示する', async () => {
      const TrackList = require('../../components/track/TrackList.jsx').default
      
      renderWithRouter(<TrackList tracks={mockSeedData.tracks} />)
      
      // 楽曲タイトルが表示されることを確認
      expect(screen.getByText('青い空の下で')).toBeInTheDocument()
      expect(screen.getByText('Digital Dreams')).toBeInTheDocument()
      
      // アーティスト名が表示されることを確認  
      expect(screen.getByText('青空バンド')).toBeInTheDocument()
      expect(screen.getByText('夜想曲')).toBeInTheDocument()
      
      // 価格が表示されることを確認
      expect(screen.getByText('¥300')).toBeInTheDocument()
      expect(screen.getByText('¥400')).toBeInTheDocument()
    })

    it('空の楽曲リストで適切なメッセージを表示する', () => {
      const TrackList = require('../../components/track/TrackList.jsx').default
      
      renderWithRouter(<TrackList tracks={[]} />)
      
      expect(screen.getByText('楽曲が見つかりませんでした')).toBeInTheDocument()
    })

    it('楽曲クリックで詳細ページに遷移する', async () => {
      const TrackList = require('../../components/track/TrackList.jsx').default
      const user = userEvent.setup()
      
      renderWithRouter(<TrackList tracks={mockSeedData.tracks} />)
      
      const trackLink = screen.getByText('青い空の下で').closest('a')
      expect(trackLink).toHaveAttribute('href', '/track/track-1')
    })
  })

  describe('TrackCard コンポーネント', () => {
    const track = mockSeedData.tracks[0]

    it('楽曲情報を正しく表示する', () => {
      const TrackCard = require('../../components/track/TrackCard.jsx').default
      
      renderWithRouter(<TrackCard track={track} />)
      
      expect(screen.getByText(track.title)).toBeInTheDocument()
      expect(screen.getByText(track.artist_name)).toBeInTheDocument()
      expect(screen.getByText(track.genre)).toBeInTheDocument()
      expect(screen.getByText(`¥${track.price}`)).toBeInTheDocument()
      expect(screen.getByText('4:05')).toBeInTheDocument() // duration formatting
    })

    it('再生ボタンクリックで音楽が再生される', async () => {
      const TrackCard = require('../../components/track/TrackCard.jsx').default
      const mockPlay = vi.fn()
      const user = userEvent.setup()
      
      renderWithProviders(<TrackCard track={track} />, {
        player: { play: mockPlay }
      })
      
      const playButton = screen.getByRole('button', { name: /再生/ })
      await user.click(playButton)
      
      expect(mockPlay).toHaveBeenCalledWith(track)
    })

    it('購入ボタンクリックで購入処理が開始される', async () => {
      const TrackCard = require('../../components/track/TrackCard.jsx').default
      const user = userEvent.setup()
      
      renderWithRouter(<TrackCard track={track} />)
      
      const purchaseButton = screen.getByRole('button', { name: /購入/ })
      await user.click(purchaseButton)
      
      // 購入確認ダイアログまたはモーダルが表示される
      expect(screen.getByText(/購入確認/)).toBeInTheDocument()
    })
  })

  // ==================== 検索コンポーネントテスト ====================
  
  describe('SearchBar コンポーネント', () => {
    it('検索クエリの入力と送信が機能する', async () => {
      const SearchBar = require('../../components/search/SearchBar.jsx').default
      const mockOnSearch = vi.fn()
      const user = userEvent.setup()
      
      renderWithRouter(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByPlaceholderText('楽曲、アーティストを検索...')
      const searchButton = screen.getByRole('button', { name: /検索/ })
      
      await user.type(searchInput, '青空')
      await user.click(searchButton)
      
      expect(mockOnSearch).toHaveBeenCalledWith('青空')
    })

    it('Enterキーで検索が実行される', async () => {
      const SearchBar = require('../../components/search/SearchBar.jsx').default
      const mockOnSearch = vi.fn()
      const user = userEvent.setup()
      
      renderWithRouter(<SearchBar onSearch={mockOnSearch} />)
      
      const searchInput = screen.getByPlaceholderText('楽曲、アーティストを検索...')
      
      await user.type(searchInput, '青空{enter}')
      
      expect(mockOnSearch).toHaveBeenCalledWith('青空')
    })

    it('空の検索クエリでは検索を実行しない', async () => {
      const SearchBar = require('../../components/search/SearchBar.jsx').default
      const mockOnSearch = vi.fn()
      const user = userEvent.setup()
      
      renderWithRouter(<SearchBar onSearch={mockOnSearch} />)
      
      const searchButton = screen.getByRole('button', { name: /検索/ })
      await user.click(searchButton)
      
      expect(mockOnSearch).not.toHaveBeenCalled()
    })
  })

  describe('SearchFilters コンポーネント', () => {
    it('ジャンルフィルターが正しく動作する', async () => {
      const SearchFilters = require('../../components/search/SearchFilters.jsx').default
      const mockOnFilterChange = vi.fn()
      const user = userEvent.setup()
      
      renderWithRouter(<SearchFilters onFilterChange={mockOnFilterChange} />)
      
      const genreSelect = screen.getByRole('combobox')
      await user.selectOptions(genreSelect, 'ポップ')
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        genre: 'ポップ'
      })
    })

    it('価格範囲フィルターが機能する', async () => {
      const SearchFilters = require('../../components/search/SearchFilters.jsx').default
      const mockOnFilterChange = vi.fn()
      const user = userEvent.setup()
      
      renderWithRouter(<SearchFilters onFilterChange={mockOnFilterChange} />)
      
      const minPriceInput = screen.getByLabelText('最低価格')
      const maxPriceInput = screen.getByLabelText('最高価格')
      
      await user.type(minPriceInput, '100')
      await user.type(maxPriceInput, '500')
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        minPrice: 100,
        maxPrice: 500
      })
    })
  })

  // ==================== 認証コンポーネントテスト ====================
  
  describe('LoginForm コンポーネント', () => {
    it('ログインフォームの送信が機能する', async () => {
      const LoginForm = require('../../components/auth/LoginForm.jsx').default
      const mockLogin = vi.fn()
      const user = userEvent.setup()
      
      renderWithProviders(<LoginForm />, {
        auth: { login: mockLogin }
      })
      
      const emailInput = screen.getByLabelText('メールアドレス')
      const passwordInput = screen.getByLabelText('パスワード')
      const submitButton = screen.getByRole('button', { name: 'ログイン' })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      })
    })

    it('バリデーションエラーが表示される', async () => {
      const LoginForm = require('../../components/auth/LoginForm.jsx').default
      const user = userEvent.setup()
      
      renderWithRouter(<LoginForm />)
      
      const submitButton = screen.getByRole('button', { name: 'ログイン' })
      await user.click(submitButton)
      
      expect(screen.getByText('メールアドレスは必須です')).toBeInTheDocument()
      expect(screen.getByText('パスワードは必須です')).toBeInTheDocument()
    })
  })

  describe('RegisterForm コンポーネント', () => {
    it('新規登録フォームが正しく動作する', async () => {
      const RegisterForm = require('../../components/auth/RegisterForm.jsx').default
      const mockRegister = vi.fn()
      const user = userEvent.setup()
      
      renderWithProviders(<RegisterForm />, {
        auth: { register: mockRegister }
      })
      
      await user.type(screen.getByLabelText('表示名'), 'テストユーザー')
      await user.type(screen.getByLabelText('メールアドレス'), 'test@example.com') 
      await user.type(screen.getByLabelText('パスワード'), 'password123')
      await user.type(screen.getByLabelText('パスワード確認'), 'password123')
      await user.selectOptions(screen.getByRole('combobox'), 'リスナー')
      
      await user.click(screen.getByRole('button', { name: '登録' }))
      
      expect(mockRegister).toHaveBeenCalledWith({
        display_name: 'テストユーザー',
        email: 'test@example.com',
        password: 'password123',
        user_role: 'LISTENER'
      })
    })

    it('パスワード確認が一致しない場合エラーが表示される', async () => {
      const RegisterForm = require('../../components/auth/RegisterForm.jsx').default
      const user = userEvent.setup()
      
      renderWithRouter(<RegisterForm />)
      
      await user.type(screen.getByLabelText('パスワード'), 'password123')
      await user.type(screen.getByLabelText('パスワード確認'), 'different')
      await user.click(screen.getByRole('button', { name: '登録' }))
      
      expect(screen.getByText('パスワードが一致しません')).toBeInTheDocument()
    })
  })

  // ==================== プレイヤーコンポーネントテスト ====================
  
  describe('AudioPlayer コンポーネント', () => {
    const mockTrack = mockSeedData.tracks[0]

    it('現在の楽曲情報を表示する', () => {
      const AudioPlayer = require('../../components/player/AudioPlayer.jsx').default
      
      renderWithProviders(<AudioPlayer />, {
        player: { currentTrack: mockTrack, isPlaying: true }
      })
      
      expect(screen.getByText(mockTrack.title)).toBeInTheDocument()
      expect(screen.getByText(mockTrack.artist_name)).toBeInTheDocument()
    })

    it('再生/一時停止ボタンが機能する', async () => {
      const AudioPlayer = require('../../components/player/AudioPlayer.jsx').default
      const mockPause = vi.fn()
      const user = userEvent.setup()
      
      renderWithProviders(<AudioPlayer />, {
        player: { 
          currentTrack: mockTrack, 
          isPlaying: true,
          pause: mockPause 
        }
      })
      
      const pauseButton = screen.getByRole('button', { name: /一時停止/ })
      await user.click(pauseButton)
      
      expect(mockPause).toHaveBeenCalled()
    })

    it('音量コントロールが動作する', async () => {
      const AudioPlayer = require('../../components/player/AudioPlayer.jsx').default
      const mockSetVolume = vi.fn()
      const user = userEvent.setup()
      
      renderWithProviders(<AudioPlayer />, {
        player: { 
          currentTrack: mockTrack,
          setVolume: mockSetVolume 
        }
      })
      
      const volumeSlider = screen.getByRole('slider', { name: /音量/ })
      fireEvent.change(volumeSlider, { target: { value: 50 } })
      
      expect(mockSetVolume).toHaveBeenCalledWith(50)
    })
  })

  // ==================== 購入関連コンポーネントテスト ====================
  
  describe('PurchaseButton コンポーネント', () => {
    const mockTrack = mockSeedData.tracks[0]

    it('購入ボタンクリックで確認ダイアログが表示される', async () => {
      const PurchaseButton = require('../../components/purchase/PurchaseButton.jsx').default
      const user = userEvent.setup()
      
      renderWithRouter(<PurchaseButton track={mockTrack} />)
      
      const purchaseButton = screen.getByRole('button', { name: /購入/ })
      await user.click(purchaseButton)
      
      expect(screen.getByText(/購入確認/)).toBeInTheDocument()
      expect(screen.getByText(`${mockTrack.title}を¥${mockTrack.price}で購入しますか？`)).toBeInTheDocument()
    })

    it('購入確認で決済処理が開始される', async () => {
      const PurchaseButton = require('../../components/purchase/PurchaseButton.jsx').default
      const user = userEvent.setup()
      
      mockAPI.post.mockResolvedValue({
        data: { id: 'purchase-1', status: 'completed' }
      })
      
      renderWithRouter(<PurchaseButton track={mockTrack} />)
      
      await user.click(screen.getByRole('button', { name: /購入/ }))
      await user.click(screen.getByRole('button', { name: '購入確定' }))
      
      expect(mockAPI.post).toHaveBeenCalledWith('/purchases/', {
        track_id: mockTrack.id,
        amount: mockTrack.price,
        payment_method: 'CREDIT_CARD',
        payment_token: expect.any(String)
      })
    })
  })

  // ==================== アーティスト関連コンポーネントテスト ====================
  
  describe('ArtistProfile コンポーネント', () => {
    const mockArtist = mockSeedData.artists[0]

    it('アーティスト情報を正しく表示する', () => {
      const ArtistProfile = require('../../components/artist/ArtistProfile.jsx').default
      
      renderWithRouter(<ArtistProfile artist={mockArtist} />)
      
      expect(screen.getByText(mockArtist.display_name)).toBeInTheDocument()
      expect(screen.getByText(`${mockArtist.track_count}曲`)).toBeInTheDocument()
    })

    it('アーティストの楽曲一覧が表示される', async () => {
      const ArtistProfile = require('../../components/artist/ArtistProfile.jsx').default
      
      mockAPI.get.mockResolvedValue({
        data: mockSeedData.tracks.filter(t => t.artist_id === mockArtist.id)
      })
      
      renderWithRouter(<ArtistProfile artist={mockArtist} />)
      
      await waitFor(() => {
        expect(screen.getByText('楽曲一覧')).toBeInTheDocument()
      })
    })
  })

  // ==================== エラーハンドリングテスト ====================
  
  describe('エラーハンドリング', () => {
    it('API エラー時にエラーメッセージが表示される', async () => {
      const TrackList = require('../../components/track/TrackList.jsx').default
      
      mockAPI.get.mockRejectedValue(new Error('API Error'))
      
      renderWithRouter(<TrackList />)
      
      await waitFor(() => {
        expect(screen.getByText('楽曲の読み込みに失敗しました')).toBeInTheDocument()
      })
    })

    it('ネットワークエラー時に適切なメッセージが表示される', async () => {
      const SearchResults = require('../../components/search/SearchResults.jsx').default
      
      mockAPI.get.mockRejectedValue(new Error('Network Error'))
      
      renderWithRouter(<SearchResults query="test" />)
      
      await waitFor(() => {
        expect(screen.getByText('ネットワークエラーが発生しました')).toBeInTheDocument()
      })
    })
  })

  // ==================== アクセシビリティテスト ====================
  
  describe('アクセシビリティ', () => {
    it('適切なARIAラベルが設定されている', () => {
      const TrackCard = require('../../components/track/TrackCard.jsx').default
      const track = mockSeedData.tracks[0]
      
      renderWithRouter(<TrackCard track={track} />)
      
      const playButton = screen.getByRole('button', { name: /再生/ })
      expect(playButton).toHaveAttribute('aria-label', `${track.title}を再生`)
      
      const purchaseButton = screen.getByRole('button', { name: /購入/ })
      expect(purchaseButton).toHaveAttribute('aria-label', `${track.title}を購入`)
    })

    it('キーボードナビゲーションが機能する', async () => {
      const SearchBar = require('../../components/search/SearchBar.jsx').default
      const user = userEvent.setup()
      
      renderWithRouter(<SearchBar />)
      
      const searchInput = screen.getByRole('textbox')
      
      // Tabキーでフォーカス移動
      await user.tab()
      expect(searchInput).toHaveFocus()
      
      // Enterキーで検索実行
      await user.type(searchInput, 'test{enter}')
      // 検索が実行されることを確認（実装に依存）
    })
  })
})