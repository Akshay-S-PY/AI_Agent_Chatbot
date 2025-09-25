
# Includes:
# 1) Groq as default provider
# 2) History trimming (last N turns)
# 3) Retries + fallback from OpenAI -> Groq on errors (e.g., rate limit)

import os
import streamlit as st

# Lang* imports
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from langchain_core.messages import AIMessage, BaseMessage

# --- Read provider SDKs inside the builder to keep imports light ---
# (Still safe to import at top; this just reduces startup noise on Cloud.)

# ---------- Secrets / env ----------
# Streamlit Cloud: st.secrets; local: .env (optional)
for k in ("OPENAI_API_KEY", "GROQ_API_KEY", "TAVILY_API_KEY"):
    if k in st.secrets:
        os.environ[k] = st.secrets[k]

# ---------- App config ----------
st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("🤖 AI Chatbot Agents")
st.caption("Create and interact with your LangGraph + LangChain agent")

# ---------- Sidebar (models) ----------
st.sidebar.header("Model Settings")

# (1) Make Groq the default provider
PROVIDERS = ["Groq", "OpenAI"]
provider = st.sidebar.radio("Provider", PROVIDERS, index=0)  # Groq default

MODEL_GROQ = ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
MODEL_OPENAI = ["gpt-4o-mini"]

model_name = st.sidebar.selectbox(
    "Model",
    MODEL_GROQ if provider == "Groq" else MODEL_OPENAI,
    index=0,
)

allow_web_search = st.sidebar.checkbox("Enable Tavily web search", value=False)

# ---------- Session state ----------
if "history" not in st.session_state:
    st.session_state.history: list[dict] = []  # [{role, content}]
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "Act as a smart, friendly AI chatbot."
if "clear_next" not in st.session_state:
    st.session_state.clear_next = False

# ---------- System prompt with button (no Ctrl+Enter) ----------
with st.form("sys_form", clear_on_submit=False):
    sys_val = st.text_area(
        "System prompt (defines your agent’s behavior)",
        value=st.session_state.system_prompt,
        height=80,
    )
    apply_sys = st.form_submit_button("Apply system prompt ✅")

if apply_sys:
    st.session_state.system_prompt = sys_val
    st.success("System prompt updated.")

st.markdown("### Chat")

# ---------- Chat form (Send button, compact spacing) ----------
default_msg = "" if st.session_state.clear_next else ""
with st.form("chat_form", clear_on_submit=False):
    user_msg = st.text_area("Your message", value=default_msg, height=120, placeholder="Ask anything…")
    c1, c2 = st.columns([1, 1])
    send = c1.form_submit_button("Send 🚀")
    clear = c2.form_submit_button("Clear chat 🧹")

# ---------- Agent builder ----------
def build_agent(selected_provider: str, selected_model: str):
    # Import the chosen LLM here (keeps top-level imports minimal)
    if selected_provider == "Groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(model=selected_model, max_retries=2, timeout=60)
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=selected_model, max_retries=2, timeout=60)

    tools = [TavilySearch(max_results=3)] if allow_web_search else []
    return create_react_agent(model=llm, tools=tools)

# ---------- Single turn with history trimming + fallback ----------
def run_turn(user_input: str) -> str:
    # (2) Trim history: keep only last N turns to control tokens
    MAX_TURNS = 6
    recent = st.session_state.history[-MAX_TURNS:]

    messages = [("system", st.session_state.system_prompt)]
    messages += [(m["role"], m["content"]) for m in recent]
    messages += [("user", user_input)]

    # Try chosen provider first
    try:
        agent = build_agent(provider, model_name)
        result = agent.invoke({"messages": messages})
    except Exception as e:
        # (3) Fallback if the chosen provider is OpenAI (common rate limits)
        if provider == "OpenAI":
            try:
                st.info("OpenAI error / rate limit — switching to Groq fallback.")
                fallback_provider = "Groq"
                fallback_model = "llama-3.1-8b-instant"
                agent = build_agent(fallback_provider, fallback_model)
                result = agent.invoke({"messages": messages})
            except Exception as e2:
                return f"⚠️ Both providers failed: {e2}"
        else:
            return f"⚠️ Request failed: {e}"

    msgs: list[BaseMessage] = result.get("messages", [])
    for m in reversed(msgs):
        if isinstance(m, AIMessage):
            return m.content
    return msgs[-1].content if msgs else "(no response)"

# ---------- Clear / Send handlers ----------
if clear:
    st.session_state.history = []
    st.session_state.clear_next = True
    st.rerun()

if send and user_msg.strip():
    st.session_state.history.append({"role": "user", "content": user_msg})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = run_turn(user_msg)
            st.session_state.history.append({"role": "assistant", "content": answer})
    st.session_state.clear_next = True
    st.rerun()
else:
    st.session_state.clear_next = False

# ---------- Render history once ----------
for m in st.session_state.history:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])
