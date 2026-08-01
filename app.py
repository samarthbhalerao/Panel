import streamlit as st
import streamlit.components.v1 as components
import json

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="JBIMS MSc Finance - Live AI Panel",
    page_icon="🏛️",
    layout="wide"
)

# Your Groq API Key hardcoded directly for instant access
GROQ_API_KEY = "Gsk_6ZDRL9heyQrMBzUtzJd0WGdyb3FY8RgqpAgkNAP6e5SfybzL9MLq"

# ---------------------------------------------------------
# 2. Web Application (3D Avatar + Lip Sync + Real AI Engine)
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
        
        <!-- Header & Countdown Timer -->
        <div class="flex justify-between items-center glass p-4 rounded-xl">
            <div>
                <h1 class="text-xl font-bold text-blue-400">🏛️ JBIMS MSc Finance — Live Reactive Panel</h1>
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

        <!-- Controls -->
        <div class="flex flex-wrap justify-center gap-4">
            <button id="start-btn" onclick="startInterview()" class="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition">
                ▶️ Start Interview
            </button>
            <button id="mic-btn" onclick="toggleMic()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition disabled:opacity-50" disabled>
                🎤 Speak Answer
            </button>
            <button id="submit-btn" onclick="submitAndThink()" class="bg-purple-600 hover:bg-purple-500 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition disabled:opacity-50" disabled>
                🧠 Submit & Next Question
            </button>
        </div>

        <!-- Live Candidate Transcript -->
        <div class="glass p-4 rounded-xl">
            <p class="text-xs text-slate-400 font-semibold mb-1">YOUR SPOKEN ANSWER TRANSCRIPT:</p>
            <p id="user-transcript" class="text-sm italic text-slate-300">Your spoken response will display here in real time...</p>
        </div>

    </div>

    <script>
        const GROQ_API_KEY = "{GROQ_API_KEY}";
        let currentQuestionCount = 1;
        let isSpeaking = false;
        let timerInterval;
        let timeLeft = 60;
        let conversationHistory = [
            {{
                role: "system",
                content: "You are a sharp, analytical senior panelist conducting an interview for JBIMS MSc Finance. Assess the candidate rigorously on finance concepts, RBI monetary policy, valuation, stock markets, or corporate finance. Ask ONE question at a time. Keep your spoken responses under 35 words so they remain punchy and clear. Begin by welcoming them and asking them to introduce themselves and their quantitative background."
            }}
        ];

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

        // --- 2. Voice Playback (Speech Synthesis) ---
        function speakText(text) {{
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance(text);
            msg.rate = 1.0;
            msg.lang = 'en-US';
            msg.onstart = () => {{ isSpeaking = true; }};
            msg.onend = () => {{ isSpeaking = false; }};
            window.speechSynthesis.speak(msg);
        }}

        // --- 3. Countdown Timer ---
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
                    submitAndThink();
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
        let currentAnswerText = "";

        if (SpeechRecognition) {{
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.lang = 'en-US';

            recognition.onresult = (e) => {{
                currentAnswerText = "";
                for (let i = 0; i < e.results.length; i++) {{
                    currentAnswerText += e.results[i][0].transcript + " ";
                }}
                document.getElementById('user-transcript').innerText = `"${{currentAnswerText.trim()}}"`;
                document.getElementById('submit-btn').disabled = false;
            }};

            recognition.onend = () => {{
                isListening = false;
                document.getElementById('mic-btn').innerText = "🎤 Speak Answer";
            }};
        }}

        function toggleMic() {{
            if (!recognition) return alert("Speech recognition is supported in Google Chrome. Please switch to Chrome.");
            if (isListening) {{
                recognition.stop();
            }} else {{
                recognition.start();
                isListening = true;
                document.getElementById('mic-btn').innerText = "🛑 Recording...";
            }}
        }}

        // --- 5. Real-Time Groq AI Call ---
        async function fetchAIResponse() {{
            document.getElementById('question-text').innerText = "Panelist is evaluating your answer and thinking...";
            try {{
                const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {{
                    method: "POST",
                    headers: {{
                        "Authorization": `Bearer ${{GROQ_API_KEY}}`,
                        "Content-Type": "application/json"
                    }},
                    body: JSON.stringify({{
                        model: "llama-3.3-70b-versatile",
                        messages: conversationHistory,
                        temperature: 0.7
                    }})
                }});
                const data = await res.json();
                const aiReply = data.choices[0].message.content;
                
                conversationHistory.push({{ role: "assistant", content: aiReply }});
                
                document.getElementById('question-text').innerText = aiReply;
                speakText(aiReply);
                startTimer();

            }} catch (err) {{
                document.getElementById('question-text').innerText = "Error connecting to AI panel. Please refresh.";
            }}
        }}

        function startInterview() {{
            document.getElementById('start-btn').disabled = true;
            document.getElementById('mic-btn').disabled = false;
            fetchAIResponse();
        }}

        function submitAndThink() {{
            clearInterval(timerInterval);
            if (isListening) recognition.stop();

            if (currentQuestionCount >= 5) {{
                const closingMsg = "Thank you. That concludes your JBIMS MSc Finance interview panel today. We wish you the best!";
                document.getElementById('question-text').innerText = closingMsg;
                speakText(closingMsg);
                document.getElementById('mic-btn').disabled = true;
                document.getElementById('submit-btn').disabled = true;
                return;
            }}

            const answer = currentAnswerText.trim() || "The candidate provided no answer within the time limit.";
            conversationHistory.push({{ role: "user", content: answer }});
            
            currentQuestionCount++;
            document.getElementById('progress-tag').innerText = `Question ${{currentQuestionCount}} / 5`;
            document.getElementById('user-transcript').innerText = "Your spoken response will display here in real time...";
            currentAnswerText = "";
            document.getElementById('submit-btn').disabled = true;

            fetchAIResponse();
        }}

        window.onload = init3D;
    </script>
</body>
</html>
"""

components.html(app_html, height=850, scrolling=True)

