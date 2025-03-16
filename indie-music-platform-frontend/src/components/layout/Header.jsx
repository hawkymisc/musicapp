import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaSearch, FaUser } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';

const HeaderContainer = styled.header`
  background-color: #343a40;
  color: white;
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
`;

const NavLink = styled(Link)`
  color: ${props => props.active ? '#ffffff' : '#cccccc'};
  text-decoration: none;
  margin: 0 1rem;
  font-size: 1rem;
  
  &:hover {
    color: #ffffff;
  }
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
`;

const ArtistBadge = styled.div`
  background-color: #007bff;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-right: 1rem;
`;

const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
`;

const Header = ({ activePage }) => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const handleAvatarClick = () => {
    // ユーザーメニューの表示などの処理
    // MVPフェーズではシンプルに実装
    if (window.confirm('ログアウトしますか？')) {
      logout();
      navigate('/login');
    }
  };

  return (
    <HeaderContainer>
      <Logo>INDIE MUSIC</Logo>
      
      <Nav>
        <NavLink to="/" active={activePage === 'home' ? 1 : 0}>ホーム</NavLink>
        <NavLink to="/search" active={activePage === 'search' ? 1 : 0}>検索</NavLink>
        {user?.type === 'artist' ? (
          <NavLink to="/artist/dashboard" active={activePage === 'artist' ? 1 : 0}>
            アーティストパネル
          </NavLink>
        ) : (
          <NavLink to="/library" active={activePage === 'library' ? 1 : 0}>
            マイライブラリ
          </NavLink>
        )}
      </Nav>
      
      <UserSection>
        {user?.type === 'artist' && <ArtistBadge>ARTIST</ArtistBadge>}
        <UserAvatar onClick={handleAvatarClick}>
          {user ? user.displayName?.charAt(0).toUpperCase() : <FaUser />}
        </UserAvatar>
      </UserSection>
    </HeaderContainer>
  );
};

export default Header;
