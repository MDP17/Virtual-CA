document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const recordButton = document.getElementById('recordButton');
    const recordingStatus = document.getElementById('recordingStatus');
    const textQuery = document.getElementById('textQuery');
    const submitTextButton = document.getElementById('submitText');
    const transcriptionBox = document.getElementById('transcriptionBox');
    const transcriptionText = document.getElementById('transcriptionText');
    const responseBox = document.getElementById('responseBox');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorBox = document.getElementById('errorBox');
    const errorText = document.getElementById('errorText');
    const toggleLangButton = document.getElementById('toggleLang');
    const langDisplay = document.getElementById('langDisplay');

    // Application state
    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let currentLanguage = 'en'; // Default language (English)

    // Initialize language display
    updateLanguageElements();

    // Function to toggle language between English and Hindi
    toggleLangButton.addEventListener('click', () => {
        currentLanguage = currentLanguage === 'en' ? 'hi' : 'en';
        langDisplay.textContent = currentLanguage === 'en' ? 'English' : 'हिंदी';
        updateLanguageElements();
        
        // Update placeholder text for input
        if (currentLanguage === 'en') {
            textQuery.placeholder = 'Type your question here...';
        } else {
            textQuery.placeholder = 'अपना प्रश्न यहां टाइप करें...';
        }
    });

    // Function to update language display based on selected language
    function updateLanguageElements() {
        const showElements = document.querySelectorAll(`.lang-${currentLanguage}`);
        const hideElements = document.querySelectorAll(`.lang-${currentLanguage === 'en' ? 'hi' : 'en'}`);
        
        showElements.forEach(el => el.style.display = 'inline');
        hideElements.forEach(el => el.style.display = 'none');
    }

    // Function to show error message
    function showError(message) {
        errorText.textContent = message;
        errorBox.classList.remove('d-none');
        loadingIndicator.classList.add('d-none');
    }

    // Function to hide error message
    function hideError() {
        errorBox.classList.add('d-none');
    }

    // Function to show loading indicator
    function showLoading() {
        loadingIndicator.classList.remove('d-none');
        hideError();
    }

    // Function to hide loading indicator
    function hideLoading() {
        loadingIndicator.classList.add('d-none');
    }

    // Function to display response
    function displayResponse(response) {
        // Format and render the response text 
        // Convert line breaks to <br> tags and ensure lists are properly displayed
        const formattedResponse = response
            .replace(/\n\n/g, '</p><p>') // Convert double line breaks to new paragraphs
            .replace(/\n/g, '<br>'); // Convert single line breaks to <br>
            
        responseBox.innerHTML = `<p>${formattedResponse}</p>`;
        hideLoading();
    }

    // Function to display transcription
    function displayTranscription(text) {
        transcriptionText.textContent = text;
        transcriptionBox.classList.remove('d-none');
    }

    // Function to start recording
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.addEventListener('dataavailable', event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            });
            
            mediaRecorder.addEventListener('stop', () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioToServer(audioBlob);
            });
            
            // Start recording with a 10-second maximum duration
            mediaRecorder.start();
            isRecording = true;
            
            // Update UI to show recording state
            recordButton.classList.add('recording');
            if (currentLanguage === 'en') {
                recordingStatus.textContent = 'Recording... (click to stop)';
            } else {
                recordingStatus.textContent = 'रिकॉर्डिंग चल रही है... (रोकने के लिए क्लिक करें)';
            }
            
            // Auto-stop after 10 seconds if still recording
            setTimeout(() => {
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    stopRecording();
                }
            }, 10000);
            
        } catch (err) {
            console.error('Error accessing microphone:', err);
            showError(currentLanguage === 'en' 
                ? 'Could not access microphone. Please check your browser permissions.' 
                : 'माइक्रोफोन तक पहुंच नहीं सकता। कृपया अपने ब्राउज़र अनुमतियों की जांच करें।');
        }
    }

    // Function to stop recording
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            
            // Update UI to show stopped state
            recordButton.classList.remove('recording');
            if (currentLanguage === 'en') {
                recordingStatus.textContent = 'Processing your recording...';
            } else {
                recordingStatus.textContent = 'आपकी रिकॉर्डिंग पर काम हो रहा है...';
            }
            
            // Show loading indicator
            showLoading();
        }
    }

    // Function to send audio to server
    function sendAudioToServer(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('language', currentLanguage);
        
        fetch('/process_voice', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(currentLanguage === 'en' 
                    ? 'Failed to process voice. Please try again.' 
                    : 'आवाज़ को प्रोसेस करने में विफल। कृपया पुनः प्रयास करें।');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Show transcription
            displayTranscription(data.transcription);
            
            // Show response
            displayResponse(data.response);
            
            // Reset recording status
            if (currentLanguage === 'en') {
                recordingStatus.textContent = 'Click to speak';
            } else {
                recordingStatus.textContent = 'बोलने के लिए क्लिक करें';
            }
        })
        .catch(error => {
            console.error('Error processing voice:', error);
            showError(error.message);
            
            // Reset recording status
            if (currentLanguage === 'en') {
                recordingStatus.textContent = 'Click to speak';
            } else {
                recordingStatus.textContent = 'बोलने के लिए क्लिक करें';
            }
        });
    }

    // Function to send text query to server
    function sendTextQuery(query) {
        showLoading();
        hideError();
        transcriptionBox.classList.add('d-none');
        
        fetch('/process_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                language: currentLanguage
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(currentLanguage === 'en' 
                    ? 'Failed to process query. Please try again.' 
                    : 'क्वेरी प्रोसेस करने में विफल। कृपया पुनः प्रयास करें।');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Show response
            displayResponse(data.response);
        })
        .catch(error => {
            console.error('Error processing text query:', error);
            showError(error.message);
        });
    }

    // Event listeners
    recordButton.addEventListener('click', () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });
    
    submitTextButton.addEventListener('click', () => {
        const query = textQuery.value.trim();
        
        if (query) {
            sendTextQuery(query);
        } else {
            showError(currentLanguage === 'en' 
                ? 'Please enter a question.' 
                : 'कृपया एक प्रश्न दर्ज करें।');
        }
    });
    
    // Allow Enter key to submit query
    textQuery.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = textQuery.value.trim();
            
            if (query) {
                sendTextQuery(query);
            } else {
                showError(currentLanguage === 'en' 
                    ? 'Please enter a question.' 
                    : 'कृपया एक प्रश्न दर्ज करें।');
            }
        }
    });
});
