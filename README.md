# 🤖 LangGraph AI Agent Chatbot

An AI chatbot powered by **LangGraph** + **LangChain** with support for:
- **Groq** models (`llama-3.1-8b-instant`, `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`)
- **OpenAI** models (`gpt-4o-mini`)
- **Tavily** web search integration

The project includes:
- **FastAPI backend** (`backend.py`) to handle requests and run the agent
- **LangGraph agent builder** (`ai_agent.py`)
- **Streamlit frontend** (`frontend.py`) for a simple chat UI
- `.env.example` to manage API keys

---

## 🚀 Features
- Multi-turn chat with memory (conversation history kept on frontend)
- Configurable **system prompt** to define agent behavior
- Optional **web search** via Tavily
- Easily switch between Groq and OpenAI models
- Clean FastAPI + Swagger docs for testing API directly

---

## 📦 Installation

### 1. Clone the repo
bash
git clone https://github.com/<your-username>/AI_Agent_Chatbot.git
cd AI_Agent_Chatbot

2. Create a virtual environment

Windows (PowerShell):

python -m venv .venv
.\.venv\Scripts\Activate.ps1


Linux / macOS:

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies
pip install -U pip
pip install -r requirements.txt

4. Configure environment variables

Copy .env.example → .env and fill in your real API keys:

OPENAI_API_KEY=sk-yourkey
GROQ_API_KEY=gsk-yourkey
TAVILY_API_KEY=tvly-yourkey

▶️ Usage
Run the backend (FastAPI)
uvicorn backend:app --reload --host 127.0.0.1 --port 9999


API docs available at: http://127.0.0.1:9999/docs

Example request body for /chat:

{
  "model_name": "llama-3.1-8b-instant",
  "model_provider": "Groq",
  "system_prompt": "Act as a smart, friendly AI chatbot.",
  "messages": [
    { "role": "user", "content": "What is FastAPI?" }
  ],
  "allow_search": false
}

Run the frontend (Streamlit)

In a new terminal (same environment):

streamlit run frontend.py


Open: http://localhost:8501

🗂 Project Structure
AI_Agent_Chatbot/
│── ai_agent.py      # Helper to build and run LangGraph agent
│── backend.py       # FastAPI backend with /chat endpoint
│── frontend.py      # Streamlit UI
│── requirements.txt # Dependencies
│── .env.example     # Example env variables
│── README.md        # Project docs

🔒 Security

Never commit .env (already ignored in .gitignore).

Only share .env.example with placeholders.

Store real keys locally or in GitHub Secrets for CI/CD.

