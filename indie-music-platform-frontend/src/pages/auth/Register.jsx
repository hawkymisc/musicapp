import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { AuthContext } from '../../contexts/AuthContext';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
`;

const Card = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 2rem;
  color: #212529;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Select = styled.select`
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  background-color: white;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Button = styled.button`
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  
  &:hover {
    background-color: #0056b3;
  }
  
  &:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
  }
`;

const LoginLink = styled.div`
  text-align: center;
  margin-top: 1rem;
  
  a {
    color: #007bff;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  text-align: center;
  margin-bottom: 1rem;
`;

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    displayName: '',
    userType: 'listener'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { register } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError('パスワードが一致しません');
      return;
    }
    
    if (formData.password.length < 6) {
      setError('パスワードは6文字以上で入力してください');
      return;
    }
    
    setLoading(true);
    
    try {
      await register(formData);
      navigate('/');
    } catch (error) {
      setError(error.message || '登録に失敗しました');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Container>
      <Card>
        <Title>新規登録</Title>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <Form onSubmit={handleSubmit}>
          <Input
            type="text"
            name="displayName"
            placeholder="表示名"
            value={formData.displayName}
            onChange={handleChange}
            required
          />
          
          <Input
            type="email"
            name="email"
            placeholder="メールアドレス"
            value={formData.email}
            onChange={handleChange}
            required
          />
          
          <Input
            type="password"
            name="password"
            placeholder="パスワード"
            value={formData.password}
            onChange={handleChange}
            required
          />
          
          <Input
            type="password"
            name="confirmPassword"
            placeholder="パスワード確認"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
          
          <Select
            name="userType"
            value={formData.userType}
            onChange={handleChange}
            required
          >
            <option value="listener">リスナー</option>
            <option value="artist">アーティスト</option>
          </Select>
          
          <Button type="submit" disabled={loading}>
            {loading ? '登録中...' : '登録'}
          </Button>
        </Form>
        
        <LoginLink>
          すでにアカウントをお持ちですか？ <Link to="/login">ログイン</Link>
        </LoginLink>
      </Card>
    </Container>
  );
};

export default Register;
