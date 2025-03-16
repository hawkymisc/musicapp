import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// 開発環境ではモックAPIを使用
import { setupMockApi } from './mockApi.js'
if (import.meta.env.DEV) {
  setupMockApi()
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)