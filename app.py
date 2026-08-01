import streamlit as st
import streamlit.components.v1 as components
import json

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="JBIMS MSc Finance - AI Interactive Simulator",
    page_icon="🏛️",
    layout="wide"
)

# ---------------------------------------------------------
# 2. Top 5 Targeted JBIMS MSc Finance Questions
# ---------------------------------------------------------
QUESTIONS = [
    "Welcome to JBIMS MSc Finance. Please introduce yourself and highlight your quantitative and financial background.",
    "Why do you want to pursue MSc Finance specifically at Jamnalal Bajaj instead of a standard MBA program?",
    "Explain the main practical differences between NPV and IRR. Which method would you trust if they give conflicting signals?",
    "How does an increase in the RBI repo rate impact stock market valuations and corporate balance sheets?",
    "How would you value an early-stage, high-growth unprofitable fintech startup versus a mature bank?"
]

# ---------------------------------------------------------
# 3. Interactive Web Application (HTML + JS + CSS + 3D)
# ---------------------------------------------------------
app_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #0f172a; color: white; font-family: system-ui, -apple-system, sans-serif; overflow-x: hidden; }}
        #canvas-container {{ width: 100%; height: 320px; position: relative; background: #1e293b; border-radius: 1rem; overflow: hidden; }}
        .glass {{ background: rgba(30, 41, 59, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="max-w-4xl mx-auto space-y-6">
        
        <!-- Header & Timer Bar -->
        <div class="flex justify-between items-center glass p-4 rounded-xl">
            <div>
                <h1 class="text-xl font-bold text-blue-400">🏛️ JBIMS MSc Finance — AI Panel</h1>
                <span id="progress-tag" class="text-xs text-slate-400 font-semibold">Question 1 / 5</span>
            </div>
            <div class="flex items-center space-x-3">
                <span class="text-xs font-semibold text-slate-400">ANSWER TIMER:</span>
                <div id="timer-display" class="text-2xl font-mono font-bold text-emerald-400 bg-slate-900 px-4 py-1 rounded-lg border border-emerald-500/30">60s</div>
            </div>
        </div>

        <!-- 3D Lip-Sync Tutor Canvas -->
        <div id="canvas-container"></div>

        <!-- Dialogue Box -->
        <div class="glass p-6 rounded-xl space-y-2">
            <p id="speaker" class="text-xs font-semibold text-emerald-400 uppercase tracking-widest">Panelist (Prof. Finance)</p>
            <p id="question-text" class="text-lg md:text-xl font-medium text-slate-100">Click "Start Interview" to begin your session.</p>
        </div>

        <!-- Action Controls -->
        <div class="flex flex-wrap justify-center gap-4">
            <button id="start-btn" onclick="startInterview()" class="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition">
                ▶️ Start Interview
            </button>
            <button id="mic-btn" onclick="toggleMic()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition disabled:opacity-50" disabled>
                🎤 Speak Answer
            </button>
            <button id="submit-btn" onclick="submitAnswer()" class="bg-purple-600 hover:bg-purple-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition disabled:opacity-50" disabled>
                🧠 Evaluate & Next Question
            </button>
        </div>

        <!-- Live Candidate Transcript & AI Feedback -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="glass p-4 rounded-xl">
                <p class="text-xs text-slate-400 font-semibold mb-1">YOUR ANSWER TRANSCRIPT:</p>
                <p id="user-transcript" class="text-sm italic text-slate-300">Your spoken answer will display here in real time...</p>
            </div>
            <div class="glass p-4 rounded-xl border border-blue-500/20">
                <p class="text-xs text-blue-400 font-semibold mb-1">AI PANELIST EVALUATION:</p>
                <p id="ai-evaluation" class="text-sm text-slate-200">Waiting for response...</p>
            </div>
        </div>

        <!-- Final Report Card -->
        <div id="report-card" class="hidden glass p-6 rounded-xl space-y-4 border-2 border-emerald-500">
            <h2 class="text-2xl font-bold text-emerald-400">📊 Final JBIMS Interview Scorecard</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div class="bg-slate-800 p-3 rounded-lg"><p class="text-xs text-slate-400">Overall Score</p><p id="score-val" class="text-2xl font-bold text-amber-400">88/100</p></div>
                <div class="bg-slate-800 p-3 rounded-lg"><p class="text-xs text-slate-400">Technical Finance</p><p id="tech-val" class="text-xl font-semibold text-blue-400">8.5/10</p></div>
                <div class="bg-slate-800 p-3 rounded-lg"><p class="text-xs text-slate-400">Time Management</p><p id="time-val" class="text-xl font-semibold text-purple-400">9.0/10</p></div>
                <div class="bg-slate-800 p-3 rounded-lg"><p class="text-xs text-slate-400">Completed</p><p id="complete-val" class="text-xl font-semibold text-emerald-400">5/5 Questions</p></div>
            </div>
        </div>

    </div>

    <script>
        const questions = {json.dumps(QUESTIONS)};
        let currentIdx = 0;
        let answers = [];
        let timerInterval;
        let timeLeft = 60;
        let isSpeaking = false;

        // --- 1. Three.js 3D Avatar Engine ---
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
        }}

        // --- 2. Voice Output ---
        function speakText(text) {{
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance(text);
            msg.rate = 1.0;
            msg.lang = 'en-US';
            msg.onstart = () => {{ isSpeaking = true; }};
            msg.onend = () => {{ isSpeaking = false; }};
            window.speechSynthesis.speak(msg);
        }}

        // --- 3. Timer Controls ---
        function startTimer() {{
            clearInterval(timerInterval);
            timeLeft = 60;
            updateTimerDisplay();
            timerInterval = setInterval(() => {{
                timeLeft--;
                updateTimerDisplay();
                if (timeLeft <= 0) {{
                    clearInterval(timerInterval);
                    if (isListening) recognition.stop();
                    document.getElementById('ai-evaluation').innerText = "⏱️ Time's up! Click 'Evaluate & Next Question'.";
                }}
            }}, 1000);
        }}

        function updateTimerDisplay() {{
            const el = document.getElementById('timer-display');
            el.innerText = `${{timeLeft}}s`;
            if (timeLeft <= 10) {{
                el.className = "text-2xl font-mono font-bold text-red-500 bg-slate-900 px-4 py-1 rounded-lg border border-red-500/50 animate-pulse";
            }} else {{
                el.className = "text-2xl font-mono font-bold text-emerald-400 bg-slate-900 px-4 py-1 rounded-lg border border-emerald-500/30";
            }}
        }}

        // --- 4. Speech Recognition ---
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        let isListening = false;

        if (SpeechRecognition) {{
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.lang = 'en-US';

            recognition.onresult = (e) => {{
                let currentText = "";
                for (let i = 0; i < e.results.length; i++) {{
                    currentText += e.results[i][0].transcript + " ";
                }}
                document.getElementById('user-transcript').innerText = `"${{currentText.trim()}}"`;
                answers[currentIdx] = currentText.trim();
                document.getElementById('submit-btn').disabled = false;
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
                document.getElementById('mic-btn').innerText = "🛑 Recording...";
            }}
        }}

        // --- 5. Flow Controls & AI Rule Engine ---
        function startInterview() {{
            currentIdx = 0;
            document.getElementById('start-btn').disabled = true;
            document.getElementById('mic-btn').disabled = false;
            loadQuestion();
        }}

        function loadQuestion() {{
            document.getElementById('progress-tag').innerText = `Question ${{currentIdx + 1}} / 5`;
            const q = questions[currentIdx];
            document.getElementById('question-text').innerText = q;
            document.getElementById('user-transcript').innerText = "Your spoken answer will display here in real time...";
            document.getElementById('ai-evaluation').innerText = "Panelist is listening...";
            speakText(q);
            startTimer();
        }}

        function submitAnswer() {{
            clearInterval(timerInterval);
            if (isListening) recognition.stop();

            // Client-side AI Evaluation Logic
            const answer = answers[currentIdx] || "";
            let feedback = "";

            if (answer.length < 15) {{
                feedback = "⚠️ Answer too brief. JBIMS panelists expect structured arguments with core financial terminology.";
            }} else if (answer.toLowerCase().includes("npv") || answer.toLowerCase().includes("wacc") || answer.toLowerCase().includes("repo") || answer.toLowerCase().includes("valuation")) {{
                feedback = "✅ Strong technical answer! You effectively incorporated key financial terminology and concepts.";
            }} else {{
                feedback = "👍 Good communication, but try adding deeper financial frameworks (e.g., DCF, WACC, or RBI policy mechanisms).";
            }}

            document.getElementById('ai-evaluation').innerText = feedback;
            speakText(feedback);

            setTimeout(() => {{
                if (currentIdx < questions.length - 1) {{
                    currentIdx++;
                    document.getElementById('submit-btn').disabled = true;
                    loadQuestion();
                }} else {{
                    finishInterview();
                }}
            }}, 3500);
        }}

        function finishInterview() {{
            clearInterval(timerInterval);
            document.getElementById('question-text').innerText = "Interview Completed! Review your final score and analysis below.";
            document.getElementById('progress-tag').innerText = "Completed";
            document.getElementById('mic-btn').disabled = true;
            document.getElementById('submit-btn').disabled = true;
            document.getElementById('report-card').classList.remove('hidden');

            let count = answers.filter(a => a && a.length > 10).length;
            let score = 50 + (count * 9.5);
            document.getElementById('score-val').innerText = `${{Math.round(score)}}/100`;
            document.getElementById('complete-val').innerText = `${{count}}/5 Questions`;
        }}

        window.onload = init3D;
    </script>
</body>
</html>
"""

components.html(app_html, height=1050, scrolling=True)

