import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import io from 'socket.io-client';

const socket = io('http://localhost:5173', {
  transports: ['websocket'],
  reconnectionAttempts: 3,
  reconnectionDelay: 1000,
});

const WebcamCapture = () => {
  const webcamRef = useRef(null);
  const [emotion, setEmotion] = useState('');
  const [highSpeedBlink, setHighSpeedBlink] = useState(false);
  const [microExpressions, setMicroExpressions] = useState([]);
  const [gazeDirection, setGazeDirection] = useState('');
  const [error, setError] = useState(null);
  const [isWebcamActive, setIsWebcamActive] = useState(false);

  useEffect(() => {
    socket.on('connect', () => {
      console.log('Connected to server');
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    socket.on('connect_error', (err) => {
      console.error('Connection error:', err);
    });

    socket.on('reconnect_attempt', () => {
      console.log('Reconnecting...');
    });

    socket.on('analysis_result', (data) => {
      setEmotion(data.emotion);
      setHighSpeedBlink(data.high_speed_blink);
      setMicroExpressions(data.micro_expressions);
      setGazeDirection(data.gaze_direction);
      setError(null);
    });

    socket.on('analysis_error', (data) => {
      setError(data.error);
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('connect_error');
      socket.off('reconnect_attempt');
      socket.off('analysis_result');
      socket.off('analysis_error');
    };
  }, []);

  const capture = () => {
    if (webcamRef.current && isWebcamActive) {
      const imageSrc = webcamRef.current.getScreenshot();
      console.log('Captured image:', imageSrc); // Log the captured image
      if (imageSrc) {
        socket.emit('video_frame', { image: imageSrc });
      } else {
        console.error('Failed to capture image');
      }
    } else {
      console.error('Webcam reference is null or webcam is not active');
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      capture();
    }, 1000); // Capture every second

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, [isWebcamActive]);

  return (
    <div>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width="100%"
        height="auto"
        videoConstraints={{
          width: 1280,
          height: 720,
          facingMode: "user"
        }}
        onUserMedia={() => {
          console.log('Webcam is active');
          setIsWebcamActive(true);
        }}
        onUserMediaError={(err) => {
          console.error('Webcam error:', err);
          setIsWebcamActive(false);
        }}
      />
      {emotion && <p>Emotion: {emotion}</p>}
      {highSpeedBlink && <p>High-Speed Blink Detected!</p>}
      {microExpressions.length > 0 && <p>Micro Expressions: {microExpressions.join(', ')}</p>}
      {gazeDirection && <p>Gaze Direction: {gazeDirection}</p>}
      {error && <p>Error: {error}</p>}
    </div>
  );
};

export default WebcamCapture;