# 💼 Virtual CA (AI Powered)

An AI-driven virtual Chartered Accountant assistant that helps users with **financial and legal decision-making** through real-time intelligent guidance.  
Supports both **text and voice queries**, integrates with **NLP (OpenAI API)**, and uses external APIs for legal/financial info retrieval.

---

## 🚀 Features
- 📝 **Text Query Support** – Ask financial or legal questions in plain language.  
- 🎙 **Voice Query Support** – Upload voice queries and get real-time transcriptions + AI responses.  
- 🤖 **AI-Powered Guidance** – Uses NLP (OpenAI) for natural, contextual responses.  
- 📊 **Legal/Financial Knowledge** – Fetches relevant data from external sources (`kanoon_helper`).  
- 🌍 **Multilingual Support** – Works in English and regional languages.  
- 🔒 **Secure Flask Web App** – Built with Flask and proxy configurations for deployment.  

---

## 🛠 Tech Stack
- **Backend**: Python, Flask  
- **AI/NLP**: OpenAI API  
- **Voice Processing**: Reverie API (speech-to-text)  
- **Data Sources**: Legal/financial API integrations  
- **Deployment**: Flask server (Gunicorn/Heroku/Render/Replit supported)

---

## 📂 Project Structure
virtual-ca/
│── app.py               # Flask app entry point
│── templates/           # HTML templates (home, help, etc.)
│── utils/
│   ├── openai_helper.py # Handles AI responses
│   ├── reverie_helper.py# Voice transcription
│   └── kanoon_helper.py # Legal/financial info retrieval
│── static/              # CSS/JS files
---

## ⚡ How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/virtual-ca.git
   cd virtual-ca
   
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your_api_key"
   export SESSION_SECRET="your_secret_key"
   
4. Run the app:
   ```bash
   python app.py
   
5.Open in your browser:
   http://localhost:5000

##🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.
