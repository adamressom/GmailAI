My bad, I get exactly what you mean now. You want it raw, loose, and completely un-nested without the markdown code-block wrapper enclosing the whole thing so it mimics a direct copy-paste dump.

Here is the entire text exactly as you formatted it:

GmailAI
📥 AI-powered Gmail organizer for email summarization and priority scoring

GmailAI is an intelligent inbox assistant that connects to the Gmail API and leverages Google's Gemini API to automatically summarize incoming emails, evaluate their urgency, and score their priority. It features a modern, clean dark-mode landing page to streamline your daily email triage.

Tech Stack
Python & Flask — Lightweight backend and server architecture (app.py)

Gemini API — Advanced LLM processing for automated email summarization and priority classification

Gmail API — Secure email fetching and inbox integration

HTML/CSS/JS — Responsive, minimalist dark-mode user interface

Features
Smart Summarization — Generates concise, actionable TL;DRs for long email threads.

Urgency Scoring — Evaluates message content to rank urgency and assign clear priority levels.

Dynamic Dashboard — A unified, clean interface to review organized emails without inbox clutter.

Secure Integration — Connects directly to your account using official Google OAuth protocols.

Getting Started
Prerequisites
Python 3.10+

A Google Cloud Project with the Gmail API enabled

A Google AI Studio Gemini API Key

Installation
Clone the repository:

Bash
   git clone https://github.com/adamressom/GmailAI.git
   cd GmailAI
Install the required dependencies:

Bash
   pip install -r requirements.txt
Set up your Google OAuth credentials:

Download your credentials.json file from the Google Cloud Console.

Place credentials.json in the root directory of this project.

Environment Variables
Create a .env file in the project root and add your Gemini API key:

Code snippet
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your_chosen_random_secret_key
Run Locally
Start the Flask development server:

Bash
python app.py
Open http://localhost:5000 in your browser, complete the Google OAuth verification, and view your intelligent inbox dashboard.

Project Structure
Plaintext
static/          # UI assets (CSS styling, icons)
templates/       # Flask HTML templates (dark landing page)
app.py           # Main application server, Gmail OAuth, and Gemini integration
requirements.txt # Python dependencies
