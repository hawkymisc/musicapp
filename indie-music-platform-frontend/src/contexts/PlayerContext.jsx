import React, { createContext, useState, useEffect } from 'react';
import { recordPlay } from '../services/track';

export const PlayerContext = createContext();

export const PlayerProvider = ({ children }) => {
  const [currentTrack, setCurrentTrack] = useState(null);
  const [playlist, setPlaylist] = useState([]);
  const [playHistory, setPlayHistory] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.8);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  // 現在の楽曲が変更された時の処理
  useEffect(() => {
    if (currentTrack) {
      // 再生履歴に追加
      const newHistory = [...playHistory];
      if (newHistory.findIndex(track => track.id === currentTrack.id) === -1) {
        newHistory.unshift(currentTrack);
        // 最大20曲まで保持
        if (newHistory.length > 20) {
          newHistory.pop();
        }
        setPlayHistory(newHistory);
      }
      
      // 再生カウントをAPIに記録
      recordPlay(currentTrack.id).catch(error => {
        console.error('Error recording play:', error);
      });
      
      // 再生を開始
      setIsPlaying(true);
    }
  }, [currentTrack]);

  // 次の曲を再生
  const playNext = () => {
    if (!playlist || playlist.length === 0 || !currentTrack) return;
    
    const currentIndex = playlist.findIndex(track => track.id === currentTrack.id);
    if (currentIndex < playlist.length - 1) {
      setCurrentTrack(playlist[currentIndex + 1]);
    }
  };

  // 前の曲を再生
  const playPrevious = () => {
    if (!playlist || playlist.length === 0 || !currentTrack) return;
    
    const currentIndex = playlist.findIndex(track => track.id === currentTrack.id);
    if (currentIndex > 0) {
      setCurrentTrack(playlist[currentIndex - 1]);
    }
  };

  // 再生/一時停止を切り替え
  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  // 音量を変更
  const changeVolume = (newVolume) => {
    setVolume(Math.max(0, Math.min(1, newVolume)));
  };

  // プログレスを更新
  const updateProgress = (newProgress) => {
    setProgress(newProgress);
  };

  // 楽曲の長さを設定
  const updateDuration = (newDuration) => {
    setDuration(newDuration);
  };

  const value = {
    currentTrack,
    setCurrentTrack,
    playlist,
    setPlaylist,
    playHistory,
    isPlaying,
    volume,
    progress,
    duration,
    playNext,
    playPrevious,
    togglePlay,
    changeVolume,
    updateProgress,
    updateDuration
  };

  return (
    <PlayerContext.Provider value={value}>
      {children}
    </PlayerContext.Provider>
  );
};

          