import streamlit as st
from groq import Groq

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Groq Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Groq AI Chatbot")
st.write("Simple chatbot using Streamlit + Groq API")

# -----------------------------
# Groq API Key
# -----------------------------
api_key = st.sidebar.text_input(
    "Enter Groq API Key",
    type="password"
)

if not api_key:
    st.info("Please enter your Groq API key in the sidebar.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# Initialize Chat History
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        }
    ]

# -----------------------------
# Display Previous Messages
# -----------------------------
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# -----------------------------
# Chat Input
# -----------------------------
user_input = st.chat_input("Type your message...")

if user_input:

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=st.session_state.messages,
                    temperature=0.7,
                    max_tokens=1024
                )

                assistant_response = response.choices[0].message.content

                st.markdown(assistant_response)

                # Save response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })

            except Exception as e:
                st.error(f"Error: {e}")

# -----------------------------
# Clear Chat Button
# -----------------------------
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        }
    ]
    st.rerun()
