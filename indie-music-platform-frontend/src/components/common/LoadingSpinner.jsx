import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const SpinnerContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.size === 'small' ? '1rem' : '2rem'};
`;

const Spinner = styled.div`
  border: ${props => props.size === 'small' ? '2px' : '4px'} solid #f3f3f3;
  border-top: ${props => props.size === 'small' ? '2px' : '4px'} solid #007bff;
  border-radius: 50%;
  width: ${props => props.size === 'small' ? '20px' : '40px'};
  height: ${props => props.size === 'small' ? '20px' : '40px'};
  animation: ${spin} 1s linear infinite;
`;

const LoadingText = styled.p`
  margin-left: 1rem;
  color: #666;
  font-size: ${props => props.size === 'small' ? '0.9rem' : '1rem'};
`;

const LoadingSpinner = ({ size = 'normal', text = '読み込み中...' }) => {
  return (
    <SpinnerContainer size={size}>
      <Spinner size={size} />
      {text && <LoadingText size={size}>{text}</LoadingText>}
    </SpinnerContainer>
  );
};

export default LoadingSpinner;