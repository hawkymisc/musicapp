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
  const [isShuffled, setIsShuffled] = useState(false);
  const [repeatMode, setRepeatMode] = useState('none'); // 'none', 'track', 'playlist'
  const [shuffledPlaylist, setShuffledPlaylist] = useState([]);

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

  // プレイリストをシャッフル
  const shuffleArray = (array) => {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  };

  // シャッフルのON/OFF
  const toggleShuffle = () => {
    const newShuffled = !isShuffled;
    setIsShuffled(newShuffled);
    
    if (newShuffled) {
      // シャッフルON: プレイリストをシャッフル
      const shuffled = shuffleArray(playlist);
      setShuffledPlaylist(shuffled);
    } else {
      // シャッフルOFF: シャッフルプレイリストをクリア
      setShuffledPlaylist([]);
    }
  };

  // リピートモードの切り替え
  const toggleRepeat = () => {
    const modes = ['none', 'track', 'playlist'];
    const currentIndex = modes.indexOf(repeatMode);
    const nextIndex = (currentIndex + 1) % modes.length;
    setRepeatMode(modes[nextIndex]);
  };

  // 次の曲を再生
  const playNext = () => {
    if (!playlist || playlist.length === 0 || !currentTrack) return;
    
    const activePlaylist = isShuffled ? shuffledPlaylist : playlist;
    const currentIndex = activePlaylist.findIndex(track => track.id === currentTrack.id);
    
    if (repeatMode === 'track') {
      // 現在の曲をリピート
      setCurrentTrack(currentTrack);
      return;
    }
    
    if (currentIndex < activePlaylist.length - 1) {
      // 次の曲へ
      setCurrentTrack(activePlaylist[currentIndex + 1]);
    } else if (repeatMode === 'playlist') {
      // プレイリストの最初に戻る
      setCurrentTrack(activePlaylist[0]);
    }
  };

  // 前の曲を再生
  const playPrevious = () => {
    if (!playlist || playlist.length === 0 || !currentTrack) return;
    
    const activePlaylist = isShuffled ? shuffledPlaylist : playlist;
    const currentIndex = activePlaylist.findIndex(track => track.id === currentTrack.id);
    
    if (currentIndex > 0) {
      setCurrentTrack(activePlaylist[currentIndex - 1]);
    } else if (repeatMode === 'playlist') {
      // プレイリストの最後に移動
      setCurrentTrack(activePlaylist[activePlaylist.length - 1]);
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
    isShuffled,
    repeatMode,
    playNext,
    playPrevious,
    togglePlay,
    toggleShuffle,
    toggleRepeat,
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

          