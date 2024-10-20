import React, { useState, useEffect } from 'react';
// import AWS from 'aws-sdk/global';
// import TranscribeService from 'aws-sdk/clients/transcribeservice';

const StoC = () => {
//     const [transcript, setTranscript] = useState('');
    
//     if (typeof window !== 'undefined' && !window.global) {
//         window.global = window;
//     }

//     useEffect(() => {
//         // Configure AWS SDK
//         AWS.config.update({
//             region: 'us-west-2' // Change to your region
//         });

//         AWS.config.credentials = new AWS.Credentials(
//             process.env.REACT_APP_AWS_ACCESS_KEY_ID, // Replace with your access key
//             process.env.REACT_APP_AWS_SECRET_ACCESS_KEY // Replace with your secret key
//         );
//         // Ensure the environment variables are loaded
//         if (!process.env.REACT_APP_AWS_ACCESS_KEY_ID || !process.env.REACT_APP_AWS_SECRET_ACCESS_KEY) {
//             console.error('AWS credentials are not set in the environment variables.');
//             return;
//         }
        

//         const transcribeService = new AWS.TranscribeService();

//         const params = {
//             LanguageCode: 'en-US', // Change to your language code
//             MediaFormat: 'mp3', // Change to your media format
//             Media: {
//                 MediaFileUri: '' // Replace with your media file URI
//             },
//             TranscriptionJobName: 'TranscriptionJob' // Change to your job name
//         };

//         transcribeService.startTranscriptionJob(params, (err, data) => {
//             if (err) console.log(err, err.stack);
//             else {
//                 const jobName = data.TranscriptionJob.TranscriptionJobName;
//                 const checkStatus = setInterval(() => {
//                     transcribeService.getTranscriptionJob({ TranscriptionJobName: jobName }, (err, data) => {
//                         if (err) console.log(err, err.stack);
//                         else {
//                             if (data.TranscriptionJob.TranscriptionJobStatus === 'COMPLETED') {
//                                 clearInterval(checkStatus);
//                                 fetch(data.TranscriptionJob.Transcript.TranscriptFileUri)
//                                     .then(response => response.json())
//                                     .then(data => setTranscript(data.results.transcripts[0].transcript));
//                             }
//                         }
//                     });
//                 }, 5000);
//             }
//         });
//     }, []);

//     return (
//         <div className="chat-container">
//             <h2>Live Transcript</h2>
//             <div className="transcript">
//                 {transcript}
//             </div>
//         </div>
//     );
    const [transcript, setTranscript] = useState('');

    const handleFileChange = (event) => {
        // Handle file change logic here
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        // Handle file upload logic here
    };

    return (
        <div className="container">
            <div className="chat-container">
                <h2>Live Transcript</h2>
                <div className="transcript">
                    {transcript}
                </div>
            </div>
        </div>
    );

};

export default StoC;