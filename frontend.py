# frontend.py
import requests
import streamlit as st

API_URL = "http://127.0.0.1:9999/chat"

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("🤖 AI Chatbot Agents")
st.caption("Create and interact with your LangGraph + LangChain agent")

# ------------------ Sidebar: provider + model ------------------
st.sidebar.header("Model Settings")
PROVIDERS = ["Groq", "OpenAI"]
provider = st.sidebar.radio("Provider", PROVIDERS, index=0)

MODEL_NAMES_GROQ = ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]
model_name = (
    st.sidebar.selectbox("Groq model", MODEL_NAMES_GROQ, index=0)
    if provider == "Groq"
    else st.sidebar.selectbox("OpenAI model", MODEL_NAMES_OPENAI, index=0)
)
allow_web_search = st.sidebar.checkbox("Enable Tavily web search", value=False)

# ------------------ Session state ------------------
if "history" not in st.session_state:
    st.session_state.history = []         # list of {"role","content"}
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "Act as a smart, friendly AI chatbot."
if "clear_next" not in st.session_state:
    st.session_state.clear_next = False    # flag to clear message textarea on next render

# ------------------ System prompt with a button ------------------
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
    # no rerun needed; prompt is stored in session

# ------------------ Chat form (Send button, compact spacing) ------------------
st.markdown("### Chat")

# Decide default value for textarea based on clear flag
default_msg = "" if st.session_state.clear_next else ""

with st.form("chat_form", clear_on_submit=False):
    user_msg = st.text_area("Your message", value=default_msg, height=120, placeholder="Ask anything…")
    col1, col2 = st.columns([1, 1])
    send = col1.form_submit_button("Send 🚀")
    clear = col2.form_submit_button("Clear chat 🧹")

def call_backend(messages):
    payload = {
        "model_name": model_name,
        "model_provider": provider,
        "system_prompt": st.session_state.system_prompt,
        "messages": messages,          # [{role, content}, ...]
        "allow_search": allow_web_search,
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=120)
        if not resp.ok:
            try:
                err = resp.json()
            except Exception:
                err = {"detail": resp.text}
            return f"⚠️ {resp.status_code}: {err}"
        data = resp.json()
        return data.get("answer", str(data))
    except Exception as e:
        return f"⚠️ Request failed: {e}"

# Handle Clear (single source of truth; no widget key mutation)
if clear:
    st.session_state.history = []
    st.session_state.clear_next = True     # clear textarea on next render
    st.rerun()

# Handle Send (no duplicate responses; render history once at the end)
if send and user_msg.strip():
    st.session_state.history.append({"role": "user", "content": user_msg})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = call_backend(st.session_state.history)
            st.session_state.history.append({"role": "assistant", "content": answer})
    # tell the next render to show empty textarea (no direct session key mutation error)
    st.session_state.clear_next = True
    st.rerun()
else:
    # if we didn't send, keep the current textarea content
    st.session_state.clear_next = False

# Render history exactly once (prevents “two responses”)
for m in st.session_state.history:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])
