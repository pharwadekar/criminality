import React from 'react';
import WebcamCapture from './components/WebcamCapture';
import InputDocuments from './components/InputDoc/InputDocuments';
import StoC from './components/speechToChat/StoC';
import './App.css';

const App = () => {
  return (
    <div className="container">
      <h1 className="header">Emotion Tracker</h1>
      <div className="content">
        <div className="component1">
          <WebcamCapture />
        </div>
        <div className="component2">
          <InputDocuments />
          <div style={{ padding: '10px' }} />
          <StoC />
        </div>
      </div>
    </div>
  );
};

export default App;