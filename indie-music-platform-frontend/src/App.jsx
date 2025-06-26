import React from 'react';
import { createGlobalStyle } from 'styled-components';
import AppRouter from './router';

// グローバルスタイル
const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  body {
    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    line-height: 1.5;
    color: #212529;
    background-color: #f5f5f5;
  }
  
  a {
    color: #007bff;
    text-decoration: none;
    
    &:hover {
      color: #0056b3;
    }
  }
  
  button {
    cursor: pointer;
  }

  /* Loading states */
  .loading-skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
  }

  @keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  /* Responsive containers */
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  @media (max-width: 768px) {
    .container {
      padding: 0 0.5rem;
    }
  }

  /* Accessible focus styles */
  button:focus-visible,
  input:focus-visible,
  textarea:focus-visible,
  select:focus-visible {
    outline: 2px solid #007bff;
    outline-offset: 2px;
  }
`;

const App = () => {
  return (
    <>
      <GlobalStyle />
      <AppRouter />
    </>
  );
};

export default App;
