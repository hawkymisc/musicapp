import React, { useState, useEffect, useRef, useContext } from 'react';
import styled from 'styled-components';
import { FaPlay, FaPause, FaStepForward, FaStepBackward, FaVolumeUp } from 'react-icons/fa';
import { Howl } from 'howler';
import { PlayerContext } from '../../contexts/PlayerContext';

const PlayerContainer = styled.div`
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 70px;
  background-color: #343a40;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 1rem;
`;

const TrackInfo = styled.div`
  display: flex;
  align-items: center;
  width: 30%;
`;

const TrackImage = styled.div`
  width: 50px;
  height: 50px;
  background-color: #6c757d;
  margin-right: 1rem;
`;

const TrackDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const TrackTitle = styled.div`
  font-size: 0.9rem;
  color: white;
`;

const ArtistName = styled.div`
  font-size: 0.8rem;
  color: #adb5bd;
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40%;
`;

const ControlButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  margin: 0 1rem;
  
  &:focus {
    outline: none;
  }
`;

const PlayButton = styled(ControlButton)`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
`;

const ProgressContainer = styled.div`
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 5px;
  cursor: pointer;
`;

const ProgressBackground = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background-color: #6c757d;
`;

const ProgressBar = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background-color: white;
  width: ${props => props.width}%;
`;

const VolumeContainer = styled.div`
  display: flex;
  align-items: center;
  width: 30%;
  justify-content: flex-end;
  padding-right: 2rem;
`;

const VolumeSlider = styled.input`
  margin-left: 1rem;
  width: 100px;
`;

const Player = () => {
  const { currentTrack, setCurrentTrack, playlist, setPlaylist } = useContext(PlayerContext);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [duration, setDuration] = useState(0);
  const soundRef = useRef(null);
  const progressTimerRef = useRef(null);

  useEffect(() => {
    if (currentTrack) {
      // 前の音声をクリーンアップ
      if (soundRef.current) {
        soundRef.current.stop();
      }
      
      // 新しい音声を設定
      soundRef.current = new Howl({
        src: [currentTrack.audioFileUrl],
        html5: true,
        volume: volume,
        onload: () => {
          setDuration(soundRef.current.duration());
        },
        onend: () => {
          setPlaying(false);
          setProgress(0);
          clearInterval(progressTimerRef.current);
        }
      });
      
      if (playing) {
        soundRef.current.play();
        startProgressTimer();
      }
    }
    
    return () => {
      if (progressTimerRef.current) {
        clearInterval(progressTimerRef.current);
      }
    };
  }, [currentTrack]);

  const startProgressTimer = () => {
    if (progressTimerRef.current) {
      clearInterval(progressTimerRef.current);
    }
    
    progressTimerRef.current = setInterval(() => {
      if (soundRef.current) {
        setProgress((soundRef.current.seek() / duration) * 100);
      }
    }, 1000);
  };

  const togglePlay = () => {
    if (!currentTrack) return;
    
    if (playing) {
      soundRef.current.pause();
      clearInterval(progressTimerRef.current);
    } else {
      soundRef.current.play();
      startProgressTimer();
    }
    
    setPlaying(!playing);
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    
    if (soundRef.current) {
      soundRef.current.volume(newVolume);
    }
  };

  const handleProgressChange = (e) => {
    if (!soundRef.current) return;
    
    const clickPosition = e.nativeEvent.offsetX;
    const progressBarWidth = e.currentTarget.offsetWidth;
    const percentage = (clickPosition / progressBarWidth) * 100;
    const seekPosition = (percentage / 100) * duration;
    
    soundRef.current.seek(seekPosition);
    setProgress(percentage);
  };

  const handleNext = () => {
    if (!playlist || playlist.length === 0) return;
    
    const currentIndex = playlist.findIndex(track => track.id === currentTrack.id);
    if (currentIndex < playlist.length - 1) {
      setCurrentTrack(playlist[currentIndex + 1]);
    }
  };

  const handlePrevious = () => {
    if (!playlist || playlist.length === 0) return;
    
    const currentIndex = playlist.findIndex(track => track.id === currentTrack.id);
    if (currentIndex > 0) {
      setCurrentTrack(playlist[currentIndex - 1]);
    }
  };

  if (!currentTrack) return null;

  return (
    <PlayerContainer>
      <TrackInfo>
        <TrackImage />
        <TrackDetails>
          <TrackTitle>{currentTrack.title}</TrackTitle>
          <ArtistName>{currentTrack.artistName}</ArtistName>
        </TrackDetails>
      </TrackInfo>
      
      <Controls>
        <ControlButton onClick={handlePrevious}>
          <FaStepBackward />
        </ControlButton>
        <PlayButton onClick={togglePlay}>
          {playing ? <FaPause /> : <FaPlay />}
        </PlayButton>
        <ControlButton onClick={handleNext}>
          <FaStepForward />
        </ControlButton>
      </Controls>
      
      <VolumeContainer>
        <FaVolumeUp />
        <VolumeSlider
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={volume}
          onChange={handleVolumeChange}
        />
      </VolumeContainer>
      
      <ProgressContainer onClick={handleProgressChange}>
        <ProgressBackground />
        <ProgressBar width={progress} />
      </ProgressContainer>
    </PlayerContainer>
  );
};

export default Player;
