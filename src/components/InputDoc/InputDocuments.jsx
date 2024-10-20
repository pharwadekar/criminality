import React, { useState } from 'react';
import axios from 'axios';

const InputDoc = () => {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert('Please select a file first!');
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      const content = e.target.result;
      const lines = content.split('\n');
      const name = lines[0];
      const testimonial = lines[1];
      const evidence = lines.slice(2).join('\n');

      const data = {
        name,
        testimonial,
        evidence,
      };

      try {
        const response = await axios.post('/api/process', data, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        setResponse(response.data);
        console.log('File processed successfully:', response.data);
      } catch (error) {
        console.error('Error processing file:', error);
      }
    };

    reader.readAsText(file);
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleFileUpload}>Upload File</button>
      {response && <div>Response: {JSON.stringify(response)}</div>}
    </div>
  );
};

export default InputDoc;