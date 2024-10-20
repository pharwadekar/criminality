// src/WebcamCapture.js

import React, { useEffect, useRef, useState } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

const WebcamCapture = () => {
  const webcamRef = useRef(null);
  const [emotion, setEmotion] = useState('');
  const [blinkDetected, setBlinkDetected] = useState(false);
  const [twitchDetected, setTwitchDetected] = useState(false);

  const capture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();

    try {
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        image: imageSrc,
      });

      if (response.data.success) {
        setEmotion(response.data.emotion);
        // Check for additional data flags like blinks or twitches
        if (response.data.blinkDetected) {
          setBlinkDetected(true);
        } else {
          setBlinkDetected(false);
        }
        
        if (response.data.twitchDetected) {
          setTwitchDetected(true);
        } else {
          setTwitchDetected(false);
        }
      }
    } catch (error) {
      console.error('Error capturing image:', error);
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      capture();
    }, 3000); // Capture every 3 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  return (
    <div>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={640}
        height={480}
      />
      <h2>Detected Emotion: {emotion}</h2>
      {blinkDetected && <h3>Blink Detected!</h3>}
      {twitchDetected && <h3>Twitch Detected!</h3>}
    </div>
  );
};

export default WebcamCapture;
