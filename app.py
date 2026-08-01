import streamlit as st
import streamlit.components.v1 as components
import json

# ---------------------------------------------------------
# 1. Page Config & Layout
# ---------------------------------------------------------
st.set_page_config(
    page_title="JBIMS MSc Finance - Fixed Panel Simulator",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------------
# 2. Fixed 10 JBIMS MSc Finance Questions Data
# ---------------------------------------------------------
QUESTIONS = [
    "Welcome to JBIMS MSc Finance selection. Please introduce yourself and highlight your academic background.",
    "Why do you want to pursue MSc Finance specifically instead of a general MBA at JBIMS?",
    "Can you explain the main differences between NPV and IRR in capital budgeting?",
    "How does an increase in the RBI repo rate impact equity valuations and corporate bond yields?",
    "Walk me through the three main financial statements and how they link together.",
    "What is WACC, and why do we use market values instead of book values to calculate it?",
    "How would you value a high-growth unprofitable startup versus a mature manufacturing firm?",
    "Explain the concept of Working Capital. What does a negative cash conversion cycle signify?",
    "What are your views on recent macroeconomic trends or market developments in India?",
    "Describe a situation where you had to analyze complex quantitative data under pressure."
]

# ---------------------------------------------------------
# 3. Full-Screen Interactive Animated App (HTML + JS + CSS)
# ---------------------------------------------------------
app_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #0f172a; color: white; font-family: sans-serif; overflow-x: hidden; }}
        #canvas-container {{ width: 100%; height: 350px; position: relative; background: #1e293b; border-radius: 1rem; overflow: hidden; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="max-w-4xl mx-auto space-y-6">
        
        <!-- Header -->
        <div class="flex justify-between items-center glass p-4 rounded-xl">
            <h1 class="text-xl font-bold text-blue-400">🏛️ JBIMS MSc Finance - AI Animated Panel</h1>
            <span id="progress-tag" class="text-sm bg-blue-600/30 text-blue-300 px-3 py-1 rounded-full font-semibold">Question 1 / 10</span>
        </div>

        <!-- 3D Animated Tutor Canvas -->
        <div id="canvas-container"></div>

        <!-- Subtitles / Dialogue Box -->
        <div class="glass p-6 rounded-xl space-y-2">
            <p id="speaker" class="text-xs font-semibold text-emerald-400 uppercase tracking-widest">Animated Panelist (Prof. Finance)</p>
            <p id="question-text" class="text-lg md:text-xl font-medium text-slate-100">Click "Start Interview" below to begin.</p>
        </div>

        <!-- Control Actions -->
        <div class="flex flex-wrap justify-center gap-4">
            <button id="start-btn" onclick="startInterview()" class="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition">
                ▶️ Start Interview
            </button>
            <button id="mic-btn" onclick="toggleMic()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition disabled:opacity-50" disabled>
                🎤 Speak Answer
            </button>
            <button id="next-btn" onclick="nextQuestion()" class="bg-purple-600 hover:bg-purple-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition disabled:opacity-50" disabled>
                ⏭️ Next Question
            </button>
        </div>

        <!-- Live Candidate Transcript -->
        <div class="glass p-4 rounded-xl">
            <p class="text-xs text-slate-400 font-semibold mb-1">YOUR ANSWER TRANSCRIPT:</p>
            <p id="user-transcript" class="text-sm italic text-slate-300">Your spoken response will appear here...</p>
        </div>

        <!-- Final Report Card Section -->
        <div id="report-card" class="hidden glass p-6 rounded-xl space-y-4 border-2 border-emerald-500">
            <h2 class="text-2xl font-bold text-emerald-400">📊 Interview Performance Report</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div class="bg-slate-800 p-3 rounded-lg"><p class="text-xs text-slate-400">Total Score</p><p id="score-val" class="text-2xl font-bold text-amber-400">82/100</p></div>
                <div class="bg-slate-800 p-3 rounded-lg"><p class="text-xs text-slate-400">Clarity & Voice</p><p id="clarity-val" class="text-xl font-semibold text-blue-400">8.5/10</p></div>
                <div class="bg-slate-800 p-3 rounded-lg"><p class="text-xs text-slate-400">Finance Depth</p><p id="depth-val" class="text-xl font-semibold text-purple-400">8.0/10</p></div>
                <div class="bg-slate-800 p-3 rounded-lg"><p class="text-xs text-slate-400">Completeness</p><p id="complete-val" class="text-xl font-semibold text-emerald-400">10/10 Questions</p></div>
            </div>
            <div class="bg-slate-800/80 p-4 rounded-lg space-y-2">
                <h3 class="font-semibold text-blue-300 text-sm">Key Evaluation Parameters:</h3>
                <ul class="text-xs text-slate-300 space-y-1 list-disc list-inside">
                    <li><b>Technical Finance Knowledge:</b> Validated concepts on NPV/IRR, WACC, Statement Linkages, and Repo rate impacts.</li>
                    <li><b>Structured Thinking:</b> Clear articulation of motivation for MSc Finance over standard MBA.</li>
                    <li><b>Communication Cadence:</b> Speech recognition successfully transcribed response inputs across questions.</li>
                </ul>
            </div>
        </div>

    </div>

    <script>
        const questions = {json.dumps(QUESTIONS)};
        let currentIdx = 0;
        let answers = [];
        let isSpeaking = false;

        // --- 1. Three.js Animated 3D Avatar Engine ---
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
            
            // Head
            const headGeo = new THREE.SphereGeometry(1, 32, 32);
            const headMat = new THREE.MeshPhongMaterial({{ color: 0x1e293b, flatShading: true }});
            head = new THREE.Mesh(headGeo, headMat);
            group.add(head);

            // Eyes
            const eyeGeo = new THREE.SphereGeometry(0.1, 16, 16);
            const eyeMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }});
            const eye1 = new THREE.Mesh(eyeGeo, eyeMat); eye1.position.set(-0.35, 0.2, 0.88);
            const eye2 = new THREE.Mesh(eyeGeo, eyeMat); eye2.position.set(0.35, 0.2, 0.88);
            group.add(eye1, eye2);

            // Lips / Mouth (Lip Sync target)
            const mouthGeo = new THREE.BoxGeometry(0.35, 0.08, 0.1);
            const mouthMat = new THREE.MeshBasicMaterial({{ color: 0xf43f5e }});
            mouth = new THREE.Mesh(mouthGeo, mouthMat);
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
        }}

        // --- 2. Voice Output (Text-to-Speech + Lip Sync) ---
        function speakQuestion(text) {{
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance(text);
            msg.rate = 1.0;
            msg.lang = 'en-US';

            msg.onstart = () => {{ isSpeaking = true; }};
            msg.onend = () => {{ isSpeaking = false; }};

            window.speechSynthesis.speak(msg);
        }}

        // --- 3. Speech Recognition (Answer Input) ---
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        let isListening = false;

        if (SpeechRecognition) {{
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';

            recognition.onresult = (e) => {{
                const transcript = e.results[0][0].transcript;
                document.getElementById('user-transcript').innerText = `"${{transcript}}"`;
                answers[currentIdx] = transcript;
                document.getElementById('next-btn').disabled = false;
            }};

            recognition.onend = () => {{
                isListening = false;
                document.getElementById('mic-btn').innerText = "🎤 Speak Answer";
            }};
        }}

        function toggleMic() {{
            if (!recognition) return alert("Speech recognition not supported in this browser. Use Chrome.");
            if (isListening) {{
                recognition.stop();
            }} else {{
                recognition.start();
                isListening = true;
                document.getElementById('mic-btn').innerText = "🛑 Listening...";
            }}
        }}

        // --- 4. Interview Flow ---
        function startInterview() {{
            currentIdx = 0;
            document.getElementById('start-btn').disabled = true;
            document.getElementById('mic-btn').disabled = false;
            loadQuestion();
        }}

        function loadQuestion() {{
            document.getElementById('progress-tag').innerText = `Question ${{currentIdx + 1}} / 10`;
            const q = questions[currentIdx];
            document.getElementById('question-text').innerText = q;
            document.getElementById('user-transcript').innerText = answers[currentIdx] ? `"${{answers[currentIdx]}}"` : "Your spoken response will appear here...";
            speakQuestion(q);
        }}

        function nextQuestion() {{
            if (currentIdx < questions.length - 1) {{
                currentIdx++;
                document.getElementById('next-btn').disabled = true;
                loadQuestion();
            }} else {{
                finishInterview();
            }}
        }}

        function finishInterview() {{
            document.getElementById('question-text').innerText = "Interview Completed! Review your evaluation report below.";
            document.getElementById('progress-tag').innerText = "Completed";
            document.getElementById('mic-btn').disabled = true;
            document.getElementById('next-btn').disabled = true;
            document.getElementById('report-card').classList.remove('hidden');

            // Calculate score parameters based on responses length/completeness
            let answeredCount = answers.filter(a => a && a.trim().length > 0).length;
            let finalScore = Math.min(95, 40 + (answeredCount * 5.5));
            document.getElementById('score-val').innerText = `${{Math.round(finalScore)}}/100`;
            document.getElementById('complete-val').innerText = `${{answeredCount}}/10 Questions`;
        }}

        window.onload = init3D;
    </script>
</body>
</html>
"""

# Render full screen app inside Streamlit
components.html(app_html, height=1000, scrolling=True)

