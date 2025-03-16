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
