import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import Header from '../components/layout/Header.jsx'

// Mock React Router
vi.mock('react-router-dom', () => ({
  Link: ({ children, to }) => <a href={to}>{children}</a>,
  useNavigate: () => vi.fn(),
}))

// Mock React Context
const mockContextValue = {
  user: {
    displayName: 'Test User',
    type: 'listener'
  },
  logout: vi.fn()
}

vi.mock('react', async () => {
  const actual = await vi.importActual('react')
  return {
    ...actual,
    useContext: () => mockContextValue
  }
})

describe('Header Component', () => {
  it('renders the logo', () => {
    render(<Header activePage="home" />)
    expect(screen.getByText('INDIE MUSIC')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    render(<Header activePage="home" />)
    expect(screen.getByText('ホーム')).toBeInTheDocument()
    expect(screen.getByText('検索')).toBeInTheDocument()
    expect(screen.getByText('マイライブラリ')).toBeInTheDocument()
  })

  it('displays user avatar with initial', () => {
    render(<Header activePage="home" />)
    expect(screen.getByText('T')).toBeInTheDocument() // First letter of "Test User"
  })
})