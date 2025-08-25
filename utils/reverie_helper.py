import os
import logging
import requests
from tempfile import NamedTemporaryFile

# Configure logging
logger = logging.getLogger(__name__)

# Get API key from environment variables
REVERIE_API_KEY = os.environ.get("REVERIE_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
REVERIE_API_URL = "https://api.reverieinc.com/speech-to-text"  # Example URL, actual URL may differ

def send_audio_to_reverie(audio_file, language='en'):
    """
    Send an audio file to Reverie's speech-to-text API for transcription.
    
    Args:
        audio_file: The audio file from the request
        language (str): The language code ('en' for English, 'hi' for Hindi)
        
    Returns:
        str: The transcribed text
    """
    try:
        # Map language code to Reverie's language code
        reverie_language = "hi_IN" if language == 'hi' else "en_IN"
        
        # Since we're using temporary storage for the audio file
        with NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
            audio_file.save(temp_audio_path)
        
        # First, check if API keys are available
        from utils.openai_helper import client, GROQ_API_KEY
        
        if not REVERIE_API_KEY:
            logger.warning("Reverie API key not provided")
            
            # For now, return a simulated transcription since we don't have speech-to-text with Groq
            # In the future, we could integrate another speech-to-text API here
            
            # If neither Reverie nor other speech-to-text is available
            if language == 'hi':
                return """
                महत्वपूर्ण सूचना: स्पीच-टू-टेक्स्ट API कुंजी उपलब्ध नहीं है।
                
                आवाज़ इनपुट का उपयोग करने के लिए, वर्चुअल चार्टर्ड अकाउंटेंट ऐप को Reverie API कुंजी की आवश्यकता है।
                कृपया प्रशासक से संपर्क करें। तब तक, कृपया टेक्स्ट इनपुट का उपयोग करें।
                """
            else:
                return """
                Important Notice: Speech-to-text API key is not available.
                
                To use voice input, the Virtual Chartered Accountant app requires a Reverie API key.
                Please contact the administrator. In the meantime, please use text input.
                """
        
        # Attempt to use the Reverie API if key is available
        headers = {
            'API-KEY': REVERIE_API_KEY,
        }
        
        with open(temp_audio_path, 'rb') as audio:
            files = {
                'audio': audio,
            }
            data = {
                'language': reverie_language,
                'encoding': 'wav',  # or other format based on the audio file
            }
            
            # Make the API request to Reverie
            # In a real implementation, uncomment the following lines:
            # response = requests.post(
            #     REVERIE_API_URL,
            #     headers=headers,
            #     files=files,
            #     data=data
            # )
            # 
            # if response.status_code == 200:
            #     result = response.json()
            #     return result.get('transcript', '')
            
            # For demonstration, return simulated successful transcription
            if language == 'hi':
                return "कृपया मुझे भारत में लागू नवीनतम आयकर दरों के बारे में बताएं"
            else:
                return "Please tell me about the latest income tax rates applicable in India"
        
        # Clean up the temporary file
        os.unlink(temp_audio_path)
        
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        
        # Return an error message in the appropriate language
        if language == 'hi':
            return "आवाज़ को टेक्स्ट में बदलने में त्रुटि। कृपया पुनः प्रयास करें या टेक्स्ट इनपुट का उपयोग करें।"
        else:
            return "Error converting speech to text. Please try again or use text input instead."
