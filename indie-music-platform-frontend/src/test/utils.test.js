import { describe, it, expect } from 'vitest'

// Simple utility functions for testing setup
function formatDuration(seconds) {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

function formatPrice(price) {
  return `¥${price.toLocaleString()}`
}

describe('Utility Functions', () => {
  describe('formatDuration', () => {
    it('formats seconds correctly', () => {
      expect(formatDuration(65)).toBe('1:05')
      expect(formatDuration(120)).toBe('2:00')
      expect(formatDuration(0)).toBe('0:00')
    })
  })

  describe('formatPrice', () => {
    it('formats price with yen symbol', () => {
      expect(formatPrice(1000)).toBe('¥1,000')
      expect(formatPrice(500)).toBe('¥500')
      expect(formatPrice(0)).toBe('¥0')
    })
  })
})