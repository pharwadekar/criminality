import React, { useState } from 'react';

const StoC = () => {
  // Step 1: Initialize state for transcribed text
  const [transcript, setTranscript] = useState('');

  // Step 2: Create a function to start speech recognition
  const startRecognition = () => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      console.log('Speech recognition started');
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          setTranscript((prevTranscript) => prevTranscript + transcriptPart);
        } else {
          interimTranscript += transcriptPart;
        }
      }
      console.log('Interim Transcript:', interimTranscript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
    };

    recognition.onend = () => {
      console.log('Speech recognition ended');
    };

    recognition.start();
  };

  return (
    <div>
      {/* Step 5: Render button to start speech recognition */}
      <button onClick={startRecognition}>Start Recognition</button>
      
      {/* Display the transcribed text */}
      <p>Transcription: {transcript}</p>
    </div>
  );
};

export default StoC;