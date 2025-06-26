import React from 'react';
import styled from 'styled-components';

const SkeletonContainer = styled.div`
  padding: 1rem;
`;

const SkeletonItem = styled.div`
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: ${props => props.rounded ? '50%' : '4px'};
  width: ${props => props.width || '100%'};
  height: ${props => props.height || '20px'};
  margin-bottom: ${props => props.spacing || '0.5rem'};

  @keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
`;

const TrackCardSkeleton = () => (
  <SkeletonContainer>
    <SkeletonItem width="100%" height="200px" spacing="1rem" />
    <SkeletonItem width="80%" height="24px" spacing="0.5rem" />
    <SkeletonItem width="60%" height="16px" spacing="0.5rem" />
    <SkeletonItem width="40%" height="16px" />
  </SkeletonContainer>
);

const ListItemSkeleton = () => (
  <SkeletonContainer>
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <SkeletonItem width="60px" height="60px" rounded spacing="0" style={{ marginRight: '1rem' }} />
      <div style={{ flex: 1 }}>
        <SkeletonItem width="70%" height="20px" spacing="0.5rem" />
        <SkeletonItem width="50%" height="16px" />
      </div>
    </div>
  </SkeletonContainer>
);

const DashboardSkeleton = () => (
  <div>
    <SkeletonContainer>
      <SkeletonItem width="60%" height="32px" spacing="1rem" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
        <SkeletonItem width="100%" height="120px" />
        <SkeletonItem width="100%" height="120px" />
        <SkeletonItem width="100%" height="120px" />
      </div>
    </SkeletonContainer>
  </div>
);

const SkeletonLoader = ({ type = 'default', count = 1 }) => {
  const renderSkeleton = () => {
    switch (type) {
      case 'track-card':
        return <TrackCardSkeleton />;
      case 'list-item':
        return <ListItemSkeleton />;
      case 'dashboard':
        return <DashboardSkeleton />;
      default:
        return (
          <SkeletonContainer>
            <SkeletonItem width="100%" height="20px" spacing="0.5rem" />
            <SkeletonItem width="80%" height="20px" spacing="0.5rem" />
            <SkeletonItem width="60%" height="20px" />
          </SkeletonContainer>
        );
    }
  };

  return (
    <>
      {Array.from({ length: count }, (_, index) => (
        <div key={index}>{renderSkeleton()}</div>
      ))}
    </>
  );
};

export default SkeletonLoader;