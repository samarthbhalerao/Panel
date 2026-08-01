import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="JBIMS MSc Finance - Gemini Live Panel",
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
            "content": "You are a sharp, analytical senior panelist conducting a live voice interview for JBIMS MSc Finance. Assess the candidate rigorously on finance concepts, RBI monetary policy, valuation, stock markets, or corporate finance. Ask ONE question at a time. Keep your spoken responses under 30 words so the conversation flows naturally like a real phone call or live chat. Start by welcoming them and asking them to briefly introduce themselves."
        }
    ]
if "q_count" not in st.session_state:
    st.session_state.q_count = 1
if "current_ai_text" not in st.session_state:
    st.session_state.current_ai_text = "Tap 'Turn On Live Mode' below to start the conversational voice session."
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

# ---------------------------------------------------------
# 4. Groq API Call Handler
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
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
            st.session_state.history.append({"role": "assistant", "content": reply})
            st.session_state.current_ai_text = reply
        else:
            st.session_state.current_ai_text = "API Key error. Please check your key in the sidebar."
    except Exception as e:
        st.session_state.current_ai_text = f"Connection error: {e}"

# Safely process incoming live spoken answers from query params
query_params = st.query_params
if "live_spoken_answer" in query_params:
    user_audio_text = query_params["live_spoken_answer"]
    st.query_params.clear()  # Clear param immediately to avoid duplicate triggers
    
    if user_audio_text.strip():
        st.session_state.history.append({"role": "user", "content": user_audio_text.strip()})
        st.session_state.q_count += 1
        
        if st.session_state.q_count > 5:
            st.session_state.current_ai_text = "Thank you! That concludes your live interview session for JBIMS MSc Finance."
        else:
            with st.spinner("Panelist responding..."):
                call_groq_api()
        st.rerun()

# ---------------------------------------------------------
# 5. Start Button Handling
# ---------------------------------------------------------
if not st.session_state.interview_started:
    if st.button("🎙️ Turn On Live Mode", use_container_width=True):
        st.session_state.interview_started = True
        with st.spinner("Connecting to Panelist..."):
            call_groq_api()
        st.rerun()

# ---------------------------------------------------------
# 6. Interactive 3D Avatar + Single-Trigger Auto-Voice
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
        #canvas-container {{ width: 100%; height: 280px; position: relative; background: #1e293b; border-radius: 1rem; overflow: hidden; }}
        .glass {{ background: rgba(30, 41, 59, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
</head>
<body class="p-2">

    <div class="max-w-4xl mx-auto space-y-4">
        
        <div class="flex justify-between items-center glass p-4 rounded-xl">
            <div class="flex items-center space-x-2">
                <span id="status-dot" class="w-3 h-3 bg-slate-500 rounded-full"></span>
                <h1 class="text-lg font-bold text-blue-400">🏛️ JBIMS MSc Finance — Live Mode</h1>
            </div>
            <span class="text-xs bg-blue-600/30 text-blue-300 px-3 py-1 rounded-full font-semibold">Question {q_count} / 5</span>
        </div>

        <div id="canvas-container"></div>

        <div class="glass p-5 rounded-xl space-y-2 border border-blue-500/20">
            <p id="speaker-status" class="text-xs font-semibold text-emerald-400 uppercase tracking-widest">Panelist (Prof. Finance)</p>
            <p id="question-text" class="text-lg md:text-xl font-medium text-slate-100">{st.session_state.current_ai_text}</p>
        </div>

        <div class="glass p-4 rounded-xl text-center space-y-2">
            <p id="live-indicator" class="text-xs font-bold text-amber-400 uppercase tracking-wider">
                ⏸️ Idle — Ready
            </p>
            <p id="transcript-display" class="text-sm italic text-slate-300 min-h-[24px]">
                Speak naturally when the panelist finishes talking...
            </p>
        </div>

    </div>

    <script>
        const aiText = {ai_text_json};
        let isSpeaking = false;
        let isSubmitting = false; // Guard to prevent duplicate submissions
        let recognizedText = "";
        let silenceTimer = null;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;

        if (SpeechRecognition) {{
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (e) => {{
                if (isSubmitting) return; // Ignore input if already sent

                recognizedText = "";
                for (let i = 0; i < e.results.length; i++) {{
                    recognizedText += e.results[i][0].transcript + " ";
                }}
                
                document.getElementById('transcript-display').innerText = `"${{recognizedText.trim()}}"`;
                document.getElementById('live-indicator').innerText = "🔴 Listening to you...";
                document.getElementById('live-indicator').className = "text-xs font-bold text-red-400 uppercase tracking-wider animate-pulse";

                clearTimeout(silenceTimer);
                // Pause threshold: 2 seconds of silence auto-submits
                silenceTimer = setTimeout(() => {{
                    if (recognizedText.trim().length > 0 && !isSubmitting) {{
                        autoSubmitAnswer();
                    }}
                }}, 2000);
            }};

            recognition.onend = () => {{
                if (!isSpeaking && !isSubmitting && {q_count} <= 5) {{
                    try {{ recognition.start(); }} catch(e) {{}}
                }}
            }};
        }}

        function autoSubmitAnswer() {{
            if (isSubmitting) return;
            isSubmitting = true; // Lock submission
            
            clearTimeout(silenceTimer);
            if (recognition) {{
                try {{ recognition.stop(); }} catch(e) {{}}
            }}

            document.getElementById('live-indicator').innerText = "🧠 Panelist Thinking...";
            document.getElementById('live-indicator').className = "text-xs font-bold text-purple-400 uppercase tracking-wider animate-pulse";
            
            const parentUrl = new URL(window.parent.location.href);
            parentUrl.searchParams.set("live_spoken_answer", recognizedText.trim());
            window.parent.location.href = parentUrl.toString();
        }}

        function speakText(text) {{
            if (!text || text.includes("Tap 'Turn On")) return;
            
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance(text);
            msg.rate = 1.05;
            msg.lang = 'en-US';

            msg.onstart = () => {{
                isSpeaking = true;
                if (recognition) try {{ recognition.stop(); }} catch(e) {{}}
                document.getElementById('live-indicator').innerText = "🔊 Panelist Speaking...";
                document.getElementById('live-indicator').className = "text-xs font-bold text-emerald-400 uppercase tracking-wider";
                document.getElementById('status-dot').className = "w-3 h-3 bg-emerald-500 rounded-full animate-ping";
            }};

            msg.onend = () => {{
                isSpeaking = false;
                document.getElementById('status-dot').className = "w-3 h-3 bg-emerald-500 rounded-full";
                document.getElementById('live-indicator').innerText = "🎤 Listening... (Speak now)";
                document.getElementById('live-indicator').className = "text-xs font-bold text-emerald-400 uppercase tracking-wider animate-pulse";
                
                if (recognition && !isSubmitting && {q_count} <= 5) {{
                    try {{ recognition.start(); }} catch(e) {{}}
                }}
            }};

            window.speechSynthesis.speak(msg);
        }}

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

components.html(app_html, height=620, scrolling=False)

