import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. Page Config & Layout
# ---------------------------------------------------------
st.set_page_config(
    page_title="JBIMS MSc Finance - AI Selection Panel",
    page_icon="🏛️",
    layout="centered"
)

# ---------------------------------------------------------
# 2. System Instruction for JBIMS MSc Finance Interviewer
# ---------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are a senior panelist conducting an interview for the JBIMS MSc Finance (MFA) program at Jamnalal Bajaj Institute of Management Studies. 
Evaluate candidates rigorously on:
1. Corporate Finance (DCF valuation, WACC, Capital Structure, Working Capital).
2. Financial Markets & Macroeconomics (RBI Repo Rate policy, Inflation, Union Budget, M&A).
3. Financial Accounting & Statement Analysis.
4. Logic, clarity, and quantitative depth under pressure.

Guidelines:
- Maintain a professional, sharp, and analytical tone typical of top B-school interviewers.
- Briefly evaluate or critique the candidate's answer (1-2 sentences).
- Ask 1 relevant follow-up question at a time.
- Keep responses concise (under 120 words).
"""

# ---------------------------------------------------------
# 3. App Header & Title
# ---------------------------------------------------------
st.title("🏛️ JBIMS MSc Finance AI Interview Panel")
st.caption("Interactive AI Selection Panel | Built for JBIMS Aspirants")

# ---------------------------------------------------------
# 4. API Key Setup (Sidebar or Secrets)
# ---------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("🔑 Setup & Settings")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key:", type="password")
    else:
        st.success("API Key Loaded Successfully!")

if not api_key:
    st.warning("👈 Please enter your Gemini API Key in the sidebar to start the mock interview.")
    st.stop()

# ---------------------------------------------------------
# 5. Initialize Gemini Client
# ---------------------------------------------------------
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing API Client: {e}")
    st.stop()

# ---------------------------------------------------------
# 6. Initialize Chat Session State
# ---------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "model",
            "parts": ["Welcome to your JBIMS MSc Finance Selection Panel interview. Please introduce yourself and state why you want to pursue MSc Finance at Jamnalal Bajaj."]
        }
    ]

# ---------------------------------------------------------
# 7. Render Existing Chat Messages
# ---------------------------------------------------------
for message in st.session_state.chat_history:
    role = "assistant" if message["role"] == "model" else "user"
    avatar = "🏛️" if role == "assistant" else "👨‍🎓"
    with st.chat_message(role, avatar=avatar):
        st.write(message["parts"][0])

# ---------------------------------------------------------
# 8. User Input & Dynamic Response Generation
# ---------------------------------------------------------
if user_prompt := st.chat_input("Type your answer to the JBIMS panel..."):
    st.session_state.chat_history.append({"role": "user", "parts": [user_prompt]})
    with st.chat_message("user", avatar="👨‍🎓"):
        st.write(user_prompt)

    with st.chat_message("assistant", avatar="🏛️"):
        with st.spinner("Panelist is evaluating your response..."):
            try:
                contents = [
                    types.Content(
                        role=msg["role"],
                        parts=[types.Part.from_text(text=msg["parts"][0])]
                    )
                    for msg in st.session_state.chat_history
                ]

                # Updated to active model version: gemini-2.0-flash
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )

                reply_text = response.text
                st.write(reply_text)
                
                st.session_state.chat_history.append({"role": "model", "parts": [reply_text]})

            except Exception as err:
                st.error(f"API Error: {err}")

