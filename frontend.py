# frontend.py — one-app Streamlit demo (no FastAPI)
import os
import requests  # not used, but handy if you later call an API
import streamlit as st

# Lang* imports
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.messages import AIMessage, BaseMessage

# ---------- Secrets / env ----------
# Streamlit Cloud: st.secrets; local: .env (optional)
for k in ("OPENAI_API_KEY", "GROQ_API_KEY", "TAVILY_API_KEY"):
    if k in st.secrets:
        os.environ[k] = st.secrets[k]

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("🤖 AI Chatbot Agents")
st.caption("Create and interact with your LangGraph + LangChain agent")

# ---------- Sidebar (models) ----------
st.sidebar.header("Model Settings")
PROVIDERS = ["Groq", "OpenAI"]
provider = st.sidebar.radio("Provider", PROVIDERS, index=0)

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

# ---------- System prompt with button ----------
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

# ---------- Chat form ----------
default_msg = "" if st.session_state.clear_next else ""
with st.form("chat_form", clear_on_submit=False):
    user_msg = st.text_area("Your message", value=default_msg, height=120, placeholder="Ask anything…")
    c1, c2 = st.columns([1, 1])
    send = c1.form_submit_button("Send 🚀")
    clear = c2.form_submit_button("Clear chat 🧹")

# ---------- Build agent on demand ----------
def build_agent():
    if provider == "Groq":
        llm = ChatGroq(model=model_name)
    else:
        llm = ChatOpenAI(model=model_name)

    tools = [TavilySearch(max_results=3)] if allow_web_search else []
    return create_react_agent(model=llm, tools=tools)

def run_turn(user_input: str) -> str:
    agent = build_agent()
    # Convert our UI history into LangGraph messages (tuples)
    messages = [("system", st.session_state.system_prompt)] + [
        (m["role"], m["content"]) for m in st.session_state.history
    ] + [("user", user_input)]

    result = agent.invoke({"messages": messages})
    msgs: list[BaseMessage] = result.get("messages", [])
    # return last AI message content
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
