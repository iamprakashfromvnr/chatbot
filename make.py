import streamlit as st
from groq import Groq
import speech_recognition as sr
import pyttsx3
import base64

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Groq Voice Chatbot",
    page_icon="🤖",
    layout="centered"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    color: #00bfff;
    text-align: center;
    font-size: 40px;
    font-weight: bold;
}

.user-text {
    color: #00ff88;
}

.assistant-text {
    color: #ffcc00;
}

.info-text {
    color: #ff66cc;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🤖 JARVIS Voice Chatbot</div>',
    unsafe_allow_html=True
)

st.write(
    '<p class="info-text">Streamlit + Groq + Voice Assistant</p>',
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR SETTINGS
# =========================================================

st.sidebar.header("⚙️ Chat Settings")

# API Key
api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password"
)

if not api_key:
    st.info("Please enter your Groq API key.")
    st.stop()

client = Groq(api_key=api_key)

# =========================================================
# MODEL
# =========================================================

model = st.sidebar.selectbox(
    "Select Model",
    [
        "openai/gpt-oss-20b",
        "llama-3.1-8b-instant"
    ]
)

# =========================================================
# TEMPERATURE
# =========================================================

temperature = st.sidebar.slider(
    "🌡️ Temperature",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.1
)

st.sidebar.write(
    f"Temperature: **{temperature}**"
)

# =========================================================
# MAX TOKENS
# =========================================================

max_tokens = st.sidebar.slider(
    "Maximum Tokens",
    min_value=100,
    max_value=4096,
    value=1024,
    step=100
)

# =========================================================
# STOP SEQUENCES
# =========================================================

st.sidebar.subheader("🛑 Stop Sequences")

use_stop = st.sidebar.checkbox(
    "Enable Stop Sequence"
)

stop_sequence = st.sidebar.text_input(
    "Stop sequence",
    value="END"
)

# =========================================================
# TEXT COLORS
# =========================================================

st.sidebar.subheader("🎨 Text Colors")

user_color = st.sidebar.color_picker(
    "User Text Color",
    "#00FF88"
)

assistant_color = st.sidebar.color_picker(
    "AI Text Color",
    "#FFCC00"
)

# =========================================================
# VOICE SETTINGS
# =========================================================

st.sidebar.subheader("🎤 Voice Settings")

voice_enabled = st.sidebar.checkbox(
    "Enable Voice Output"
)

# =========================================================
# CHAT HISTORY
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Give clear and simple answers."
            )
        }
    ]

# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "system":
        continue

    if message["role"] == "user":

        with st.chat_message("user"):

            st.markdown(
                f"""
                <div style="
                    color:{user_color};
                    font-size:18px;
                    font-weight:500;
                ">
                👤 {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        with st.chat_message("assistant"):

            st.markdown(
                f"""
                <div style="
                    color:{assistant_color};
                    font-size:18px;
                    font-weight:500;
                ">
                🤖 {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================================================
# VOICE INPUT FUNCTION
# =========================================================

def get_voice_input():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            st.info("🎤 Listening... Speak now.")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        text = recognizer.recognize_google(
            audio
        )

        return text

    except sr.WaitTimeoutError:

        st.error("No speech detected.")
        return ""

    except sr.UnknownValueError:

        st.error("Could not understand your voice.")
        return ""

    except Exception as e:

        st.error(f"Microphone error: {e}")
        return ""


# =========================================================
# VOICE OUTPUT FUNCTION
# =========================================================

def speak_text(text):

    try:

        engine = pyttsx3.init()

        engine.setProperty(
            "rate",
            170
        )

        engine.setProperty(
            "volume",
            1.0
        )

        engine.say(text)

        engine.runAndWait()

    except Exception as e:

        st.error(
            f"Voice output error: {e}"
        )


# =========================================================
# VOICE INPUT BUTTON
# =========================================================

if st.button("🎤 Speak"):

    voice_text = get_voice_input()

    if voice_text:

        st.session_state.voice_input = voice_text

        st.success(
            f"You said: {voice_text}"
        )

# =========================================================
# CHAT INPUT
# =========================================================

default_input = st.session_state.get(
    "voice_input",
    ""
)

user_input = st.chat_input(
    "Type your message..."
)

# Use voice input if available
if not user_input and default_input:

    user_input = default_input

    st.session_state.voice_input = ""

# =========================================================
# PROCESS USER MESSAGE
# =========================================================

if user_input:

    # -----------------------------------------
    # Display User
    # -----------------------------------------

    with st.chat_message("user"):

        st.markdown(
            f"""
            <div style="
                color:{user_color};
                font-size:18px;
            ">
            👤 {user_input}
            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------------------
    # Save User Message
    # -----------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # -----------------------------------------
    # Prepare Stop Sequence
    # -----------------------------------------

    stop = None

    if use_stop and stop_sequence:

        stop = [
            stop_sequence
        ]

    # -----------------------------------------
    # Call Groq
    # -----------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 Thinking..."
        ):

            try:

                response = client.chat.completions.create(

                    model=model,

                    messages=st.session_state.messages,

                    temperature=temperature,

                    max_tokens=max_tokens,

                    stop=stop
                )

                answer = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                # ---------------------------------
                # Display AI Response
                # ---------------------------------

                st.markdown(
                    f"""
                    <div style="
                        color:{assistant_color};
                        font-size:18px;
                        line-height:1.6;
                    ">
                    🤖 {answer}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ---------------------------------
                # Save AI Response
                # ---------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                # ---------------------------------
                # Voice Output
                # ---------------------------------

                if voice_enabled:

                    speak_text(answer)

            except Exception as e:

                st.error(
                    f"Groq API Error: {e}"
                )

# =========================================================
# CLEAR CHAT
# =========================================================

st.sidebar.divider()

if st.sidebar.button("🗑️ Clear Chat"):

    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant."
            )
        }
    ]

    st.rerun()
