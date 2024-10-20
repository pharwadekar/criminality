import React from 'react';
import WebcamCapture from './components/WebcamCapture';
import InputDocuments from './components/InputDoc/InputDocuments';
import StoC from './components/speechToChat/StoC';
import image from './assets/image.png';
import './App.css';

const App = () => {
  return (
    <div className="container">
      <h1 className="header">
        <img src={image} alt="Court" style={{ width: '75px', height: '75px', marginRight: '50px' }} />
        Criminality
        <img src={image} alt="Court" style={{ width: '75px', height: '75px', marginLeft: '50px' }} />
      </h1>
      <div className="content">
        <div className="component component1">
          <WebcamCapture />
        </div>
        <div className="component component2">
          <InputDocuments />
          <div style={{ padding: '10px' }} />
          <StoC />
        </div>     
      </div>
    </div>
  );
};

export default App;