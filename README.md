# 🤖 AI Agent Chatbot (LangGraph + Groq + OpenAI + Tavily)

An **AI-powered chatbot** built with **LangGraph** and **LangChain**, deployed on **Streamlit Cloud**.  
It supports multiple LLM providers (**Groq, OpenAI**) and integrates **Tavily API** for real-time web search.  
The chatbot is live and functional — try it out directly from your browser!

👉 [**Live Demo on Streamlit**](https://agentbyakshay.streamlit.app)

---

## 🚀 Features
- **Dynamic AI Agents**: Built with LangGraph ReAct architecture for reasoning + tool use.
- **Multi-Model Support**:  
  - Groq → `llama-3.1-8b-instant`, `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`  
  - OpenAI → `gpt-4o-mini`
- **Real-Time Web Search**: Tavily API integration for live, up-to-date results.
- **Customizable System Prompt**: Define the agent’s role (e.g., “Act as a dietician”, “Act as an AI consultant”).
- **Chat UI**: Built with Streamlit — supports multi-turn history, clear chat, and web search toggle.
- **Error Handling**: Automatic **OpenAI → Groq fallback** on rate-limit or quota errors.
- **Deployed**: Streamlit Cloud (public URL, no local setup required to try).

---

## 🛠 Tech Stack
- **LangGraph** (ReAct agent orchestration)
- **LangChain** (LLM integrations)
- **Groq API** (Llama 3 + Mixtral models, ultra-fast inference)
- **OpenAI GPT-4o-mini**
- **Tavily API** (web search tool)
- **Streamlit** (frontend + deployment)
- **Python 3.12**
- **dotenv / Streamlit Secrets** (for key management)

---

## 📦 Local Installation (optional)

You can also run this locally if you want to develop or extend it.

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

4. Setup environment variables

Create a .env file (local only, don’t commit it) or use Streamlit secrets when deploying:

OPENAI_API_KEY=sk-yourkey
GROQ_API_KEY=gsk-yourkey
TAVILY_API_KEY=tvly-yourkey

5. Run Streamlit app
streamlit run frontend.py

🌍 Deployment (Streamlit Cloud)

Push repo to GitHub.

Go to Streamlit Cloud
 → New app.

Select your repo → frontend.py.

In Settings → Secrets, paste keys in TOML format:

OPENAI_API_KEY = "sk-yourkey"
GROQ_API_KEY = "gsk-yourkey"
TAVILY_API_KEY = "tvly-yourkey"


Deploy 🚀 Your app gets a public URL like:
https://your-app.streamlit.app

🗂 Project Structure
AI_Agent_Chatbot/
│── frontend.py       # Streamlit app
│── requirements.txt  # Dependencies
│── .env.example      # Example env vars (local dev)
│── README.md         # Project docs

🔒 Security

API keys are never hardcoded; they are loaded via .env (local) or st.secrets (Streamlit Cloud).

.env is in .gitignore to prevent accidental leaks.
