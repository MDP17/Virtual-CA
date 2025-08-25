import os
import json
import logging
from groq import Groq

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Groq client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Keep for backwards compatibility

# Create the client only if API key is available
client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq client initialized successfully")

def analyze_query(query, language='en'):
    """
    Analyze a user's query to understand what financial or legal information is needed.
    
    Args:
        query (str): The user's query in text form
        language (str): The language of the query (en or hi)
        
    Returns:
        dict: Analysis of the query including search terms and topic classification
    """
    try:
        # Check if Groq client is available
        if not client or not GROQ_API_KEY:
            logger.warning("Groq API key not provided, using default analysis")
            search_terms = ["finance", "tax", "accounting"]
            if query:
                # Get first few words as search terms if query exists
                words = query.split()
                if words:
                    search_terms = words[:3]
            
            return {
                "topic": "general",
                "search_terms": search_terms,
                "intent": "information",
                "entities": []
            }
            
        system_prompt = """
        You are a financial analysis assistant for Indian taxation and accounting. 
        Analyze the user's query to extract key information and classify the topic.
        Output a JSON with:
        1. "topic": Main financial/legal topic (taxation, GST, auditing, etc.)
        2. "search_terms": List of 3-5 search terms for legal information
        3. "intent": User's probable intent (information, calculation, advice)
        4. "entities": Any mentioned financial values, dates, or organizations
        """
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Groq's most capable model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.2  # Lower temperature for more precise analysis
            # Groq doesn't support json_response directly, we'll parse the text response
        )
        
        if response and response.choices and response.choices[0].message.content:
            analysis = json.loads(response.choices[0].message.content)
            logger.debug(f"Query analysis: {analysis}")
            return analysis
        else:
            raise ValueError("Invalid response from Groq API")
    
    except Exception as e:
        logger.error(f"Error analyzing query: {str(e)}")
        # Return a default analysis to avoid breaking the flow
        search_terms = ["finance", "tax", "accounting"]
        if query:
            search_terms = [query]
            
        return {
            "topic": "general",
            "search_terms": search_terms,
            "intent": "information",
            "entities": []
        }

def generate_ai_response(query, analysis, legal_info, language='en'):
    """
    Generate a comprehensive response to the user's query using Groq AI.
    
    Args:
        query (str): The user's original query
        analysis (dict): Analysis of the query from analyze_query
        legal_info (list): Legal information from Indian Kanoon
        language (str): The language for the response (en or hi)
        
    Returns:
        str: AI-generated response to the user's query
    """
    try:
        # Check if Groq client is available
        if not client or not GROQ_API_KEY:
            logger.warning("Groq API key not provided, using default response")
            
            # Return a message informing the user that API key is needed
            if language == 'hi':
                return """
                महत्वपूर्ण सूचना: Groq API कुंजी उपलब्ध नहीं है।
                
                इस वर्चुअल चार्टर्ड अकाउंटेंट ऐप को चलाने के लिए एक Groq API कुंजी की आवश्यकता है।
                कृपया प्रशासक से संपर्क करें और उन्हें एक वैध API कुंजी प्रदान करने के लिए कहें।
                
                आप API कुंजी प्राप्त करने के लिए https://console.groq.com पर जा सकते हैं।
                """
            else:
                return """
                Important Notice: Groq API key is not available.
                
                This Virtual Chartered Accountant app requires a Groq API key to function properly.
                Please contact the administrator to provide a valid API key.
                
                You can obtain an API key by visiting https://console.groq.com.
                """
        
        # For Hindi queries, we'll include instructions to respond in Hindi
        language_instruction = "Respond in Hindi." if language == 'hi' else "Respond in English."
        
        system_prompt = f"""
        You are a virtual Chartered Accountant specialized in Indian taxation, finance, and accounting laws.
        Provide accurate, clear, and helpful responses to user queries. 
        Include specific references to relevant Indian laws, regulations, or guidelines when applicable.
        Keep responses concise yet comprehensive.
        {language_instruction}
        
        Format your responses in a structured, easy-to-read bullet point format:
        - Use numbered points for sequential information (steps, procedures)
        - Use bullet points for key facts and information
        - Group related information together under clear headings
        - Highlight important numbers, dates, or amounts in a clear way
        - Organize information in a logical flow from general to specific
        
        Here are key principles to follow:
        1. Be factual and avoid speculation.
        2. Provide citations for legal information.
        3. Explain complex topics in simple terms.
        4. When calculations are involved, show steps clearly.
        5. Maintain a professional yet friendly tone.
        6. Do not provide outdated information - if unsure, state limitations.
        7. If the query is outside your expertise, acknowledge limitations.
        """
        
        # Prepare the legal information for the context
        legal_context = "No specific legal information found." if not legal_info else "\n".join(legal_info)
        
        # Create a comprehensive user message with all the context
        user_message = f"""
        USER QUERY: {query}
        
        QUERY ANALYSIS:
        Topic: {analysis.get('topic', 'general')}
        Intent: {analysis.get('intent', 'information')}
        
        RELEVANT LEGAL INFORMATION:
        {legal_context}
        
        Please provide a helpful response to the user's query.
        """
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Using Groq's most capable model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,  # Balanced between creativity and precision
            max_tokens=1000
        )
        
        if response and response.choices and response.choices[0].message:
            return response.choices[0].message.content
        else:
            raise ValueError("Invalid response from Groq API")
    
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        
        # Return a friendly error message in the appropriate language
        if language == 'hi':
            return "माफ़ करें, आपके प्रश्न का उत्तर देने में त्रुटि हुई है। कृपया अपना प्रश्न दोबारा पूछने का प्रयास करें या अपनी इंटरनेट कनेक्शन की जांच करें।"
        else:
            return "Sorry, there was an error processing your query. Please try asking your question again or check your internet connection."
