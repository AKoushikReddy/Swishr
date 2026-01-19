import streamlit as st

from services.get_title import *
from services.chat_util import *
from services.get_models_list import *
from db.conversation import *

st.set_page_config(
    page_title="Swishr",
    page_icon="D:\\Swishr\\icon.png",
    layout="centered"
)

# ---- Load models and set default to "gemma" ----
if "OLLAMA_MODELS" not in st.session_state:
    st.session_state.OLLAMA_MODELS = get_models_list()

if "selected_model" not in st.session_state:
    if "gemma" in st.session_state.OLLAMA_MODELS:
        st.session_state.selected_model = "gemma"
    elif st.session_state.OLLAMA_MODELS:
        st.session_state.selected_model = st.session_state.OLLAMA_MODELS[0]
    else:
        st.session_state.selected_model = "No models available"

# ---- Logo + Model name in top-right (using st.image - 100% reliable) ----
col_logo, col_model = st.columns([3, 1])

with col_logo:
    st.image("static/title.png", width=340)

with col_model:
    st.markdown(
        f"<div style='text-align: right; color: #888888; font-size: 13px; margin-top: 30px;'>"
        f"Model: {st.session_state.selected_model}</div>",
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: #333; margin-top: 20px;'>", unsafe_allow_html=True)

# ---- Session state ----
st.session_state.setdefault("conversation_id", None)
st.session_state.setdefault("conversation_title", None)
st.session_state.setdefault("chat_history", [])

# ---- Sidebar: Chat History (without "Title:" prefix) ----
with st.sidebar:
    st.header("Chat History")

    if st.button("New Chat"):
        st.session_state.conversation_id = None
        st.session_state.conversation_title = None
        st.session_state.chat_history = []

    conversations = get_all_conversations()

    for cid, title in conversations.items():
        is_current = cid == st.session_state.conversation_id

        clean_title = title.replace("Title: ", "") if title and title.startswith("Title: ") else title or "Untitled"

        label = f"**{clean_title}**" if is_current else clean_title

        if st.button(label, key=f"conv_{cid}"):
            doc = get_conversation(cid) or {}
            st.session_state.conversation_id = cid
            st.session_state.conversation_title = doc.get("title", "Untitled")
            st.session_state.chat_history = [
                {"role": m["role"], "content": m["content"]} for m in doc.get("messages", [])
            ]

# ---- Main chat container (scrollable messages) ----
chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_history:
        avatar = "👤" if msg["role"] == "user" else "🏀"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# ---- Spacer to keep input at bottom ----
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

# ---- Bottom input bar with model selector (gear icon) ----
with st.container():
    col_input, col_icon = st.columns([10, 1])

    with col_input:
        user_query = st.chat_input("Ask AI...")

    with col_icon:
        with st.popover("⚙️", use_container_width=True):
            st.caption("**Select model**")
            new_model = st.selectbox(
                "Available models",
                st.session_state.OLLAMA_MODELS,
                index=st.session_state.OLLAMA_MODELS.index(st.session_state.selected_model)
                if st.session_state.selected_model in st.session_state.OLLAMA_MODELS else 0,
                label_visibility="collapsed"
            )
            if new_model != st.session_state.selected_model:
                st.session_state.selected_model = new_model
                st.rerun()

# Current selected model
selected_model = st.session_state.selected_model

# ---- Handle user input with streaming assistant response ----
if user_query:
    # Show and save user message
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with chat_container:
        with st.chat_message("user", avatar='👤'):
            st.markdown(user_query)

    # Persist user message to DB
    if st.session_state.conversation_id is None:
        try:
            raw_title = get_chat_title(selected_model, user_query) or "New Chat"
            title = raw_title.replace("Title: ", "") if raw_title.startswith("Title: ") else raw_title
        except Exception:
            title = "New Chat"
        conv_id = create_new_conversation(title=title, role="user", content=user_query)
        st.session_state.conversation_id = conv_id
        st.session_state.conversation_title = title
    else:
        add_message(st.session_state.conversation_id, "user", user_query)

    # Stream and display assistant response
    with chat_container:
        with st.chat_message("assistant", avatar='🏀'):
            try:
                # Fixed: Added stream=True to get a generator
                response_stream = get_answer(selected_model, st.session_state.chat_history, stream=True)
                full_response = st.write_stream(response_stream)
            except Exception as e:
                full_response = f"[Error getting response: {e}]"
                st.markdown(full_response)

    # Save full assistant response AFTER streaming
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
    if st.session_state.conversation_id:
        add_message(st.session_state.conversation_id, "assistant", full_response)

    st.rerun()