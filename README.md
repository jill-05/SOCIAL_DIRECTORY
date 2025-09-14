🤖 AI Talent Matcher Dashboard
An intelligent web dashboard that uses Large Language Models (OpenAI and Google Gemini) to parse job descriptions and rank talent profiles from a CSV file. The application features a modern, interactive UI with a built-in AI assistant.

To add a screenshot, take a picture of your running application, name it REPLACE_WITH_SCREENSHOT.png, and place it in your project's root directory.

✨ Key Features
AI-Powered Ranking: Leverages LLMs to score candidates based on skills, job type preferences, and personality traits derived from their profiles.

Dual-LLM Fallback System: Intelligently tries to use the OpenAI API first and automatically falls back to the Google Gemini API on failure, ensuring high availability.

Interactive Dashboard: A clean, two-panel UI for easy input and clear visualization of the top 10 ranked candidates.

Clickable Candidate Profiles: Click on any candidate in the results list to view a detailed pop-up modal with their specific skills, job types, and platforms.

Integrated AI Assistant: A friendly, floating chatbot (powered by the same LLM backend) is available to answer user questions.

🛠️ Tech Stack
Backend: Python, Flask, Waitress

Frontend: HTML, CSS, JavaScript (no frameworks)

AI & NLP:

OpenAI API (gpt-3.5-turbo)

Google Gemini API (gemini-1.5-flash)

sentence-transformers for semantic similarity

Data Processing: Pandas

⚙️ Setup and Installation
Follow these steps to get the project running on your local machine.

1. Clone the Repository
Bash

git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
2. Create and Activate a Virtual Environment
Windows (PowerShell):

PowerShell

python -m venv .venv
.venv\Scripts\Activate.ps1
macOS / Linux:

Bash

python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Set Up Environment Variables
Create a file named .env in the root of your project directory and add your API keys:

# .env file

OPENAI_API_KEY="sk-..."
GOOGLE_API_KEY="..."
The application will still run if only one API key is provided, but the fallback functionality will be limited.

5. Run the Application
Bash

python app.py
The server will start, and you can access the dashboard in your web browser at http://127.0.0.1:8080.

🚀 How to Use
Open the web application in your browser.

Paste a detailed job description into the Search Box on the left panel.

Click the "Search Candidates" button.

The top 10 ranked candidates will appear in the middle panel.

Click on any candidate card to open a pop-up window with their full details.

Click the robot icon (🤖) at the bottom right to chat with the AI assistant for any general questions.