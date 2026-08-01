import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="JBIMS MSc Finance - Live AI Panel",
    page_icon="🏛️",
    layout="wide"
)

# ---------------------------------------------------------
# 2. Sidebar API Key Setup
# ---------------------------------------------------------
st.sidebar.title("🔑 AI Panel Setup")
groq_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password", value="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")
st.sidebar.caption("Get a free key instantly at console.groq.com")

if not groq_api_key:
    st.warning("👈 Please enter a valid Groq API Key in the left sidebar to start.")
    st.stop()

# ---------------------------------------------------------
# 3. Session State Initialization
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "system",
            "content": "You are a sharp, analytical senior panelist conducting an interview for JBIMS MSc Finance. Assess the candidate rigorously on finance concepts, RBI monetary policy, valuation, stock markets, or corporate finance. Ask ONE question at a time. Keep your spoken responses under 35 words so they remain punchy and concise. Start by introducing yourself briefly and asking the candidate to introduce themselves."
        }
    ]
if "q_count" not in st.session_state:
    st.session_state.q_count = 1
if "current_ai_text" not in st.session_state:
    st.session_state.current_ai_text = "Click 'Start Interview' to begin your live session."
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

# ---------------------------------------------------------
# 4. Groq Backend Function Call
# ---------------------------------------------------------
def call_groq_api():
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": st.session_state.history,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
            st.session_state.history.append({"role": "assistant", "content": reply})
            st.session_state.current_ai_text = reply
        else:
            st.session_state.current_ai_text = "API Key error or invalid key. Please check your Groq console."
    except Exception as e:
        st.session_state.current_ai_text = f"Connection error: {e}"

# Process input if passed back from JavaScript voice recognition
query_params = st.query_params
if "spoken_answer" in query_params:
    user_audio_text = query_params["spoken_answer"]
    st.query_params.clear() # clear URL parameter
    
    if user_audio_text.strip():
        st.session_state.history.append({"role": "user", "content": user_audio_text.strip()})
        st.session_state.q_count += 1
        
        if st.session_state.q_count > 5:
            st.session_state.current_ai_text = "Thank you. That concludes your JBIMS MSc Finance interview panel today. Best of luck!"
        else:
            with st.spinner("Panelist is thinking..."):
                call_groq_api()
        st.rerun()

# ---------------------------------------------------------
# 5. Handle Start Button
# ---------------------------------------------------------
if not st.session_state.interview_started:
    if st.button("▶️ Start Interview", use_container_width=True):
        st.session_state.interview_started = True
        with st.spinner("Panelist is preparing..."):
            call_groq_api()
        st.rerun()

# ---------------------------------------------------------
# 6. Interactive 3D Avatar + Voice Mic Interface
# ---------------------------------------------------------
ai_text_json = json.dumps(st.session_state.current_ai_text)
q_count = st.session_state.q_count

app_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #0f172a; color: white; font-family: system-ui, sans-serif; }}
        #canvas-container {{ width: 100%; height: 300px; position: relative; background: #1e293b; border-radius: 1rem; overflow: hidden; }}
        .glass {{ background: rgba(30, 41, 59, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
</head>
<body class="p-2">

    <div class="max-w-4xl mx-auto space-y-4">
        
        <!-- Header -->
        <div class="flex justify-between items-center glass p-4 rounded-xl">
            <h1 class="text-xl font-bold text-blue-400">🏛️ JBIMS MSc Finance — Live Panelist</h1>
            <span class="text-xs bg-blue-600/30 text-blue-300 px-3 py-1 rounded-full font-semibold">Question {q_count} / 5</span>
        </div>

        <!-- 3D Avatar -->
        <div id="canvas-container"></div>

        <!-- Dialogue Box -->
        <div class="glass p-5 rounded-xl space-y-2 border border-blue-500/20">
            <p class="text-xs font-semibold text-emerald-400 uppercase tracking-widest">Panelist (Prof. Finance)</p>
            <p id="question-text" class="text-lg md:text-xl font-medium text-slate-100">{st.session_state.current_ai_text}</p>
        </div>

        <!-- Mic & Voice Input Controls -->
        <div class="glass p-4 rounded-xl space-y-3 text-center">
            <div class="flex justify-center gap-4">
                <button id="mic-btn" onclick="toggleMic()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition flex items-center gap-2">
                    🎤 Start Speaking
                </button>
                <button id="submit-btn" onclick="submitSpokenAnswer()" class="bg-purple-600 hover:bg-purple-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition disabled:opacity-50" disabled>
                    🧠 Submit Answer & Continue
                </button>
            </div>
            <div>
                <p class="text-xs text-slate-400 font-semibold mb-1">LIVE VOICE TRANSCRIPT:</p>
                <p id="transcript-display" class="text-sm italic text-slate-200 min-h-[24px]">Click "Start Speaking" and talk into your microphone...</p>
            </div>
        </div>

    </div>

    <script>
        const aiText = {ai_text_json};
        let isSpeaking = false;
        let recognizedText = "";

        // --- 1. Speech Recognition Setup ---
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        let isListening = false;

        if (SpeechRecognition) {{
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.lang = 'en-US';

            recognition.onresult = (e) => {{
                recognizedText = "";
                for (let i = 0; i < e.results.length; i++) {{
                    recognizedText += e.results[i][0].transcript + " ";
                }}
                document.getElementById('transcript-display').innerText = `"${{recognizedText.trim()}}"`;
                document.getElementById('submit-btn').disabled = false;
            }};

            recognition.onend = () => {{
                isListening = false;
                document.getElementById('mic-btn').innerText = "🎤 Start Speaking";
                document.getElementById('mic-btn').className = "bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition flex items-center gap-2";
            }};
        }}

        function toggleMic() {{
            if (!recognition) {{
                alert("Speech recognition requires Google Chrome or Microsoft Edge browser.");
                return;
            }}
            if (isListening) {{
                recognition.stop();
            }} else {{
                recognition.start();
                isListening = true;
                document.getElementById('mic-btn').innerText = "🛑 Stop Recording";
                document.getElementById('mic-btn').className = "bg-red-600 hover:bg-red-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition flex items-center gap-2 animate-pulse";
            }}
        }}

        function submitSpokenAnswer() {{
            if (isListening) recognition.stop();
            const textToSend = recognizedText.trim() || "Candidate provided no spoken answer.";
            
            // Pass transcript back to Streamlit backend via URL parameters
            const parentUrl = new URL(window.parent.location.href);
            parentUrl.searchParams.set("spoken_answer", textToSend);
            window.parent.location.href = parentUrl.toString();
        }}

        // --- 2. Text to Speech Playback ---
        function speakText(text) {{
            if (!text || text.includes("Click 'Start")) return;
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance(text);
            msg.rate = 1.0;
            msg.lang = 'en-US';
            msg.onstart = () => {{ isSpeaking = true; }};
            msg.onend = () => {{ isSpeaking = false; }};
            window.speechSynthesis.speak(msg);
        }}

        // --- 3. 3D Lip-Sync Canvas ---
        let scene, camera, renderer, mouth, head;
        
        function init3D() {{
            const container = document.getElementById('canvas-container');
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0, 4.5);

            renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.8));
            const light = new THREE.DirectionalLight(0x38bdf8, 1);
            light.position.set(5, 5, 5);
            scene.add(light);

            const group = new THREE.Group();
            head = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 32), new THREE.MeshPhongMaterial({{ color: 0x1e293b, flatShading: true }}));
            group.add(head);

            const eyeGeo = new THREE.SphereGeometry(0.1, 16, 16);
            const eyeMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }});
            const eye1 = new THREE.Mesh(eyeGeo, eyeMat); eye1.position.set(-0.35, 0.2, 0.88);
            const eye2 = new THREE.Mesh(eyeGeo, eyeMat); eye2.position.set(0.35, 0.2, 0.88);
            group.add(eye1, eye2);

            mouth = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.1), new THREE.MeshBasicMaterial({{ color: 0xf43f5e }}));
            mouth.position.set(0, -0.35, 0.88);
            group.add(mouth);

            scene.add(group);

            let clock = new THREE.Clock();
            function animate() {{
                requestAnimationFrame(animate);
                let t = clock.getElapsedTime();
                group.position.y = Math.sin(t * 1.5) * 0.04;

                if (isSpeaking) {{
                    mouth.scale.y = 1 + Math.abs(Math.sin(t * 18)) * 3.5;
                    mouth.scale.x = 1 + Math.abs(Math.sin(t * 12)) * 0.4;
                }} else {{
                    mouth.scale.set(1, 1, 1);
                }}
                renderer.render(scene, camera);
            }}
            animate();
            
            speakText(aiText);
        }}

        window.onload = init3D;
    </script>
</body>
</html>
"""

components.html(app_html, height=650, scrolling=False)

