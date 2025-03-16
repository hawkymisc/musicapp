import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaUpload, FaMusic, FaImage } from 'react-icons/fa';
import { AuthContext } from '../../contexts/AuthContext';
import { uploadTrack } from '../../services/track';
import Header from '../layout/Header';

const Container = styled.div`
  min-height: 100vh;
  background-color: #f5f5f5;
`;

const Content = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
`;

const PageTitle = styled.h1`
  margin-bottom: 2rem;
  color: #343a40;
`;

const Card = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #343a40;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  min-height: 100px;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
`;

const FileInputContainer = styled.div`
  border: 2px dashed #ced4da;
  border-radius: 4px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  
  &:hover {
    border-color: #007bff;
  }
`;

const HiddenFileInput = styled.input`
  display: none;
`;

const FileIcon = styled.div`
  font-size: 2rem;
  color: #6c757d;
  margin-bottom: 1rem;
`;

const FileName = styled.div`
  margin-top: 1rem;
  color: #343a40;
  font-weight: 500;
`;

const ButtonGroup = styled.div`
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
`;

const Button = styled.button`
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
  }
  
  &:hover {
    background-color: #0069d9;
  }
  
  &:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  margin-top: 1rem;
`;

const Preview = styled.div`
  margin-top: 1rem;
  display: flex;
  align-items: center;
`;

const ImagePreview = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
  margin-right: 1rem;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const AudioPreview = styled.audio`
  width: 100%;
  margin-top: 0.5rem;
`;

const genreOptions = [
  'ポップス', 'ロック', 'ジャズ', 'クラシック', 'ヒップホップ', 'R&B', 'エレクトロニック',
  'フォーク', 'カントリー', 'ブルース', 'メタル', 'レゲエ', 'ワールド', 'その他'
];

const TrackUpload = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [genre, setGenre] = useState(genreOptions[0]);
  const [price, setPrice] = useState('300');
  const [audioFile, setAudioFile] = useState(null);
  const [coverFile, setCoverFile] = useState(null);
  const [audioPreviewUrl, setAudioPreviewUrl] = useState('');
  const [coverPreviewUrl, setCoverPreviewUrl] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleAudioSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('audio/')) {
      setError('音声ファイルを選択してください');
      return;
    }
    
    setAudioFile(file);
    setError('');
    
    // オーディオプレビューを作成
    const url = URL.createObjectURL(file);
    setAudioPreviewUrl(url);
  };
  
  const handleCoverSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
      setError('画像ファイルを選択してください');
      return;
    }
    
    setCoverFile(file);
    setError('');
    
    // 画像プレビューを作成
    const url = URL.createObjectURL(file);
    setCoverPreviewUrl(url);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title || !audioFile) {
      setError('タイトルと音声ファイルは必須です。');
      return;
    }
    
    const priceValue = parseInt(price, 10);
    if (isNaN(priceValue) || priceValue < 0) {
      setError('価格は0以上の数値を入力してください。');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('genre', genre);
      formData.append('price', priceValue);
      formData.append('audioFile', audioFile);
      if (coverFile) {
        formData.append('coverFile', coverFile);
      }
      formData.append('isPublic', isPublic);
      
      const trackId = await uploadTrack(formData);
      navigate(`/artist/tracks/${trackId}`);
    } catch (err) {
      console.error('Upload error:', err);
      setError('アップロードに失敗しました。後ほど再度お試しください。');
    } finally {
      setLoading(false);
    }
  };
  
  // クリーンアップ関数
  const cleanupPreviews = () => {
    if (audioPreviewUrl) {
      URL.revokeObjectURL(audioPreviewUrl);
    }
    if (coverPreviewUrl) {
      URL.revokeObjectURL(coverPreviewUrl);
    }
  };
  
  return (
    <Container>
      <Header activePage="artist" />
      
      <Content>
        <PageTitle>楽曲アップロード</PageTitle>
        
        <Card>
          {error && <ErrorMessage>{error}</ErrorMessage>}
          
          <Form onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="title">タイトル *</Label>
              <Input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="楽曲のタイトル"
                required
              />
            </FormGroup>
            
            <FormGroup>
              <Label htmlFor="description">説明</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="楽曲の説明、背景などを入力してください"
              />
            </FormGroup>
            
            <FormGroup>
              <Label htmlFor="genre">ジャンル</Label>
              <Select
                id="genre"
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
              >
                {genreOptions.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </Select>
            </FormGroup>
            
            <FormGroup>
              <Label htmlFor="price">価格（円）*</Label>
              <Input
                id="price"
                type="number"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="価格"
                required
              />
            </FormGroup>
            
            <FormGroup>
              <Label>音声ファイル *</Label>
              <FileInputContainer onClick={() => document.getElementById('audioFile').click()}>
                <FileIcon>
                  <FaMusic />
                </FileIcon>
                <div>クリックして音声ファイルを選択</div>
                {audioFile && <FileName>{audioFile.name}</FileName>}
                <HiddenFileInput
                  id="audioFile"
                  type="file"
                  accept="audio/*"
                  onChange={handleAudioSelect}
                />
              </FileInputContainer>
              
              {audioPreviewUrl && (
                <Preview>
                  <AudioPreview controls src={audioPreviewUrl} />
                </Preview>
              )}
            </FormGroup>
            
            <FormGroup>
              <Label>カバーアート</Label>
              <FileInputContainer onClick={() => document.getElementById('coverFile').click()}>
                <FileIcon>
                  <FaImage />
                </FileIcon>
                <div>クリックしてカバーアートを選択</div>
                {coverFile && <FileName>{coverFile.name}</FileName>}
                <HiddenFileInput
                  id="coverFile"
                  type="file"
                  accept="image/*"
                  onChange={handleCoverSelect}
                />
              </FileInputContainer>
              
              {coverPreviewUrl && (
                <Preview>
                  <ImagePreview>
                    <img src={coverPreviewUrl} alt="カバープレビュー" />
                  </ImagePreview>
                </Preview>
              )}
            </FormGroup>
            
            <FormGroup>
              <Label>公開設定</Label>
              <div>
                <input
                  id="isPublic"
                  type="checkbox"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                />
                <label htmlFor="isPublic"> この楽曲を公開する</label>
              </div>
            </FormGroup>
            
            <ButtonGroup>
              <Button type="submit" disabled={loading}>
                <FaUpload />
                {loading ? 'アップロード中...' : 'アップロード'}
              </Button>
            </ButtonGroup>
          </Form>
        </Card>
      </Content>
    </Container>
  );
};

export default TrackUpload;
