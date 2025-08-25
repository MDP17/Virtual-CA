import os
import logging
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from utils.openai_helper import generate_ai_response, analyze_query
from utils.reverie_helper import send_audio_to_reverie
from utils.kanoon_helper import fetch_legal_info

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

@app.route('/')
def home():
    """Render the main page of the virtual CA application."""
    return render_template('index.html')

@app.route('/help')
def help_page():
    """Render the help page with instructions on how to use the app."""
    return render_template('help.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    """Process text queries from the user."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        language = data.get('language', 'en')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Analyze the query to understand what it's about
        analysis = analyze_query(query, language)
        
        # Fetch relevant legal information based on the analysis
        legal_info = fetch_legal_info(analysis.get('search_terms', []))
        
        # Generate the final response using AI
        response = generate_ai_response(query, analysis, legal_info, language)
        
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error processing text query: {str(e)}")
        return jsonify({'error': f'Failed to process query: {str(e)}'}), 500

@app.route('/process_voice', methods=['POST'])
def process_voice():
    """Process voice queries from the user."""
    try:
        language = request.form.get('language', 'en')
        
        # Check if the post has the file part
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        
        # Send audio to Reverie API for transcription
        transcription = send_audio_to_reverie(audio_file, language)
        
        if not transcription:
            return jsonify({'error': 'Failed to transcribe audio'}), 500
            
        # Analyze the transcribed query
        analysis = analyze_query(transcription, language)
        
        # Fetch relevant legal information
        legal_info = fetch_legal_info(analysis.get('search_terms', []))
        
        # Generate the final response
        response = generate_ai_response(transcription, analysis, legal_info, language)
        
        return jsonify({
            'transcription': transcription,
            'response': response
        })
    except Exception as e:
        logger.error(f"Error processing voice query: {str(e)}")
        return jsonify({'error': f'Failed to process voice query: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
