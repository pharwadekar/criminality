import React, { useState } from 'react';
import axios from 'axios';
import './InputDocument.css';

const InputDocuments = () => {
    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!selectedFile) {
            alert('Please select a file first!');
            return;
        }

        const reader = new FileReader();
        reader.onload = async (e) => {
            const text = e.target.result;

            try {
                const response = await axios.post('YOUR_BACKEND_ENDPOINT/llm', { text }, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                console.log('File content sent successfully:', response.data);
            } catch (error) {
                console.error('Error sending file content:', error);
            }
        };
        try {
            reader.readAsText(selectedFile);
        } catch (error) {
            console.error('Error reading file:', error);
            alert('Error reading file. Please try again.');
        }
    };

    return (
        <div className="container1">
            <h2>Upload Evidence</h2>
            <form onSubmit={handleSubmit}>
                <input type="file" accept=".txt" onChange={handleFileChange} />
                <button type="submit">Upload</button>
            </form>
        </div>
    );
};

export default InputDocuments;