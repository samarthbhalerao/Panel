import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="JBIMS MSc Finance - AI Panel",
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
# 3. Session State Setup
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "system",
            "content": "You are a sharp, analytical senior panelist conducting an interview for JBIMS MSc Finance. Assess the candidate rigorously on finance concepts, RBI monetary policy, valuation, stock markets, or corporate finance. Ask ONE question at a time. Keep your spoken responses under 30 words so they remain punchy and clear. Begin by welcoming Samarth and asking him about his quantitative background."
        }
    ]
if "q_count" not in st.session_state:
    st.session_state.q_count = 1
if "current_ai_text" not in st.session_state:
    st.session_state.current_ai_text = "Click 'Start Interview' to begin your session."
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

# ---------------------------------------------------------
# 5. Application UI & Controls
# ---------------------------------------------------------
st.title("🏛️ JBIMS MSc Finance — Live AI Panel")

if not st.session_state.interview_started:
    if st.button("▶️ Start Interview Session", use_container_width=True, type="primary"):
        st.session_state.interview_started = True
        with st.spinner("Panelist is preparing..."):
            call_groq_api()
        st.rerun()

# ---------------------------------------------------------
# 6. Interactive 3D Avatar + Lip Sync Engine
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
        #canvas-container {{ width: 100%; height: 260px; position: relative; background: #1e293b; border-radius: 1rem; overflow: hidden; }}
        .glass {{ background: rgba(30, 41, 59, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
</head>
<body class="p-2">

    <div class="max-w-4xl mx-auto space-y-3">
        
        <div class="flex justify-between items-center glass p-3 rounded-xl">
            <h2 class="text-sm font-bold text-blue-400">JBIMS MSc Finance Panelist</h2>
            <span class="text-xs bg-blue-600/30 text-blue-300 px-3 py-1 rounded-full font-semibold">Question {q_count} / 5</span>
        </div>

        <div id="canvas-container"></div>

        <div class="glass p-4 rounded-xl border border-blue-500/20">
            <p id="speaker-status" class="text-xs font-semibold text-emerald-400 uppercase tracking-widest mb-1">Panelist (Prof. Finance)</p>
            <p id="question-text" class="text-base md:text-lg font-medium text-slate-100">{st.session_state.current_ai_text}</p>
        </div>

    </div>

    <script>
        const aiText = {ai_text_json};
        let isSpeaking = false;

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

components.html(app_html, height=430, scrolling=False)

# ---------------------------------------------------------
# 7. Clean Native Streamlit Input & Next Question Trigger
# ---------------------------------------------------------
if st.session_state.interview_started:
    st.write("---")
    candidate_answer = st.text_area(
        "🎤 Your Answer (Type or tap mic icon on your keyboard):",
        placeholder="e.g. My name is Samarth. I graduated from Pune University...",
        height=100
    )
    
    if st.button("🧠 Send Answer & Get Next Question", type="primary", use_container_width=True):
        if candidate_answer.strip():
            st.session_state.history.append({"role": "user", "content": candidate_answer.strip()})
        else:
            st.session_state.history.append({"role": "user", "content": "Candidate provided a brief introduction."})
            
        st.session_state.q_count += 1
        
        if st.session_state.q_count > 5:
            st.session_state.current_ai_text = "Thank you, Samarth. That concludes your JBIMS MSc Finance interview panel today. Best of luck!"
        else:
            with st.spinner("Panelist is thinking..."):
                call_groq_api()
        st.rerun()

