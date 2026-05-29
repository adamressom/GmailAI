# GmailAI

📥 **AI-powered Gmail organizer for email summarization and priority scoring**

GmailAI is an intelligent inbox assistant that connects to the Gmail API and uses Google's Gemini API to summarize incoming emails, evaluate urgency, and assign priority scores. It also includes a clean dark-mode landing page designed to make email triage faster and easier.

---

## Tech Stack

- **Python & Flask**: Lightweight backend and server architecture
- **Gemini API**: AI-powered email summarization and priority classification
- **Gmail API**: Secure email fetching and inbox integration
- **HTML/CSS/JavaScript**: Responsive dark-mode user interface

---

## Features

- **Smart Summarization**  
  Generates concise and actionable TL;DR summaries for long emails and threads.

- **Urgency Scoring**  
  Evaluates email content to determine urgency and assign clear priority levels.

- **Dynamic Dashboard**  
  Provides a clean interface to review organized emails without inbox clutter.

- **Secure Integration**  
  Connects to Gmail using official Google OAuth authentication.

---

## Getting Started

### Prerequisites

Before running this project, make sure you have:

- Python 3.10+
- A Google Cloud Project with the Gmail API enabled
- A Google AI Studio Gemini API key

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/adamressom/GmailAI.git
cd GmailAI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Google OAuth credentials

Download your `credentials.json` file from the Google Cloud Console.

Place the file in the root directory of this project:

```plaintext
GmailAI/
├── credentials.json
├── app.py
├── requirements.txt
├── static/
└── templates/
```

---

## Environment Variables

Create a `.env` file in the project root and add the following:

```env
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your_chosen_random_secret_key
```

---

## Run Locally

Start the Flask development server:

```bash
python app.py
```

Then open the app in your browser:

```plaintext
http://localhost:5000
```

Complete the Google OAuth verification and view your intelligent inbox dashboard.

---

## Project Structure

```plaintext
GmailAI/
├── static/              # UI assets, CSS styling, icons
├── templates/           # Flask HTML templates
├── app.py               # Main Flask app, Gmail OAuth, and Gemini integration
├── requirements.txt     # Python dependencies
├── credentials.json     # Google OAuth credentials, not included in repo
└── README.md            # Project documentation
```

---

## Security Note

Do not commit your `.env` file or `credentials.json` file to GitHub. These files contain private API keys and authentication credentials.

Make sure they are listed in your `.gitignore` file:

```gitignore
.env
credentials.json
token.json
```

---

## Author

Created by [Adam Ressom](https://github.com/adamressom)
