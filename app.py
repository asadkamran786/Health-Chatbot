## HealthBot - Educational Health Assistant
## Based on your original chatbot - customized for health use-case
## Stack: Streamlit + LangChain + Groq (openai/gpt-oss models)

import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

## Step 1: Load API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

## Helper: Load Lottie from URL
def load_lottie_url(url: str):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

def lottie_player(lottie_json, height=200, width=200, key=None, loop=True, autoplay=True):
    """Render Lottie animation using lottie-player via HTML"""
    if lottie_json is None:
        return
    # Encode JSON as string for JS
    lottie_str = json.dumps(lottie_json)
    components.html(f"""
    <div style="display:flex; justify-content:center; align-items:center;">
        <div id="lottie-{key}" style="width:{width}px; height:{height}px;"></div>
    </div>
    <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.7.5/lottie.min.js"></script>
    <script>
        var animationData = {lottie_str};
        var container = document.getElementById('lottie-{key}');
        if(container) {{
            lottie.loadAnimation({{
                container: container,
                renderer: 'svg',
                loop: {str(loop).lower()},
                autoplay: {str(autoplay).lower()},
                animationData: animationData
            }});
        }}
    </script>
    """, height=height+20, width=width+20)

# Preload Lottie animations (public free Lotties)
LOTTIE_URLS = {
    "heartbeat": "https://assets2.lottiefiles.com/packages/lf20_5njp3vys.json",  # heartbeat
    "doctor": "https://assets1.lottiefiles.com/packages/lf20_c8sz1alp.json",  # doctor
    "thinking": "https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json",  # thinking dots
    "medicine": "https://assets2.lottiefiles.com/packages/lf20_jj1qz9pb.json",  # medical
    "healthy": "https://assets1.lottiefiles.com/packages/lf20_tutvdkg0.json",  # healthy lifestyle
    "success": "https://assets10.lottiefiles.com/packages/lf20_atippm2k.json"  # success
}

## Step 2: Page config
st.set_page_config(
    page_title="HealthBot - Your Wellness Companion",
    page_icon="🩺",
    layout="wide"
)

## Step 2b: Colorful Animated Background + UI Styling
st.markdown("""
<style>
/* ===== Animated Gradient Background ===== */
.stApp {
    background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab, #8e44ad, #f39c12);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    min-height: 100vh;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Floating bubbles animation */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(circle at 20% 30%, rgba(255,255,255,0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(255,255,255,0.1) 0%, transparent 50%),
        radial-gradient(circle at 40% 80%, rgba(255,255,255,0.12) 0%, transparent 40%);
    animation: floatBubbles 20s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes floatBubbles {
    0%, 100% { transform: translateY(0px) scale(1); opacity: 0.5; }
    50% { transform: translateY(-20px) scale(1.1); opacity: 0.8; }
}

/* Make main content have glassmorphism */
.main .block-container {
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 2rem;
    margin-top: 1rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    position: relative;
    z-index: 1;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.3);
}

section[data-testid="stSidebar"] .block-container {
    background: transparent !important;
    box-shadow: none !important;
}

/* Title animation */
h1 {
    background: linear-gradient(90deg, #e73c7e, #23a6d5, #8e44ad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: titleGlow 3s ease-in-out infinite alternate;
    font-weight: 800 !important;
}

@keyframes titleGlow {
    0% { filter: brightness(1) drop-shadow(0 0 5px rgba(231,60,126,0.3)); }
    100% { filter: brightness(1.2) drop-shadow(0 0 15px rgba(35,166,213,0.4)); }
}

/* Chat messages with colorful borders */
div[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.95);
    border-radius: 15px;
    border-left: 5px solid;
    animation: slideIn 0.5s ease-out;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    border-left-color: #e73c7e;
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(231,60,126,0.05));
}

div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    border-left-color: #23a6d5;
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(35,166,213,0.05));
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Metrics with gradient */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
    border-radius: 12px;
    padding: 10px;
    border: 1px solid rgba(255,255,255,0.5);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

/* Buttons with animation */
.stButton > button {
    background: linear-gradient(90deg, #e73c7e, #23a6d5);
    color: white;
    border: none;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(231,60,126,0.3);
    background: linear-gradient(90deg, #23a6d5, #e73c7e);
}

/* Chat input */
div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.9);
    border-radius: 25px;
    border: 2px solid transparent;
    background-clip: padding-box;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

/* Expander */
.streamlit-expanderHeader {
    background: linear-gradient(90deg, rgba(231,60,126,0.1), rgba(35,166,213,0.1));
    border-radius: 10px;
}

/* Pulse animation for caption */
@keyframes pulse {
    0%, 100% { opacity: 0.8; }
    50% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

## Step 3: Title and disclaimer with Lottie Header
# Load lotties once and cache in session
if "lotties" not in st.session_state:
    with st.spinner("Loading animations..."):
        st.session_state.lotties = {}
        for name, url in LOTTIE_URLS.items():
            st.session_state.lotties[name] = load_lottie_url(url)

col_l1, col_title, col_l2 = st.columns([1, 2, 1])

with col_l1:
    if st.session_state.lotties.get("heartbeat"):
        lottie_player(st.session_state.lotties["heartbeat"], height=130, width=130, key="header_heart")

with col_title:
    st.markdown("""
    <div style="text-align:center;">
        <h1 style="font-size: 2.8rem; margin-bottom:0;">🩺 HealthBot</h1>
        <p style="font-size:1.15rem; color:white; font-weight:700; text-shadow: 0 2px 10px rgba(0,0,0,0.4);">
            Your Colorful Wellness Companion ✨
        </p>
        <p style="font-size:0.9rem; color:rgba(255,255,255,0.9); font-weight:500;">
            Education Only, Not Medical Advice
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_l2:
    if st.session_state.lotties.get("doctor"):
        lottie_player(st.session_state.lotties["doctor"], height=130, width=130, key="header_doc")

st.caption("Analytix Camp B6 | Streamlit + LangChain + Groq | Lottie Animated Edition 🌈")

# Floating mini Lottie row for visual appeal
st.markdown("""
<style>
.lottie-row {
    display: flex;
    justify-content: space-around;
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

with st.expander("⚠️ Important Disclaimer - Read before use", expanded=True):
    st.markdown("""
    **This chatbot is for educational information only.**
    - It does NOT provide diagnosis, prescriptions, or replace a doctor
    - For serious, worsening, or emergency symptoms, seek professional medical help promptly
    - Always consult a qualified healthcare professional for personal medical decisions
    - Information is general and may not apply to your specific situation
    """)

## Step 4: Check API key
if not groq_api_key:
    st.error("GROQ_API_KEY not found")
    st.info("Create a .env file in project folder and add:")
    st.code("GROQ_API_KEY=your_real_key_here", language="Text")
    st.stop()

## Step 5: Model options
model_options = {
    "GPT 20B (Fast, low cost)": "openai/gpt-oss-20b",
    "GPT 120B (More capable)": "openai/gpt-oss-120b"
}

## Step 6: Session state for memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "input_tokens" not in st.session_state:
    st.session_state.input_tokens = 0
if "output_tokens" not in st.session_state:
    st.session_state.output_tokens = 0
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

## Step 7: Sidebar controls - Health specific
with st.sidebar:
    st.header("🛠️ HealthBot Controls")
    
    # Small Lottie in sidebar
    if st.session_state.lotties.get("healthy"):
        lottie_player(st.session_state.lotties["healthy"], height=120, width=120, key="sidebar_healthy")

    selected_model_name = st.selectbox(
        "Choose AI Model",
        options=list(model_options.keys()),
        index=0
    )
    model_id = model_options[selected_model_name]

    st.subheader("Assistant Mode")
    assistant_mode = st.selectbox(
        "Focus area",
        options=[
            "General Wellness & Education",
            "Nutrition & Healthy Eating",
            "Fitness & Exercise Guidance",
            "Sleep & Stress Management",
            "First Aid Information",
            "Child Health Education",
            "Women's Health Education"
        ],
        index=0
    )

    language_pref = st.selectbox(
        "Answer Language",
        options=["English", "Urdu (Roman)", "Urdu + English Mix"],
        index=0
    )

    temperature = st.slider(
        "Creativity (Response Variability)",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Low = more focused and factual. High = more varied"
    )

    max_tokens = st.slider(
        "Maximum answer length",
        min_value=128,
        max_value=1024,
        value=512,
        step=128
    )

    st.divider()
    
    st.subheader("🎨 Visual Theme")
    theme = st.selectbox(
        "Background Animation",
        options=["Rainbow Gradient (Default)", "Ocean Breeze", "Sunset Vibes", "Forest Calm", "Aurora"],
        index=0
    )
    
    # Apply selected theme
    themes = {
        "Rainbow Gradient (Default)": "linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab, #8e44ad, #f39c12)",
        "Ocean Breeze": "linear-gradient(-45deg, #2193b0, #6dd5ed, #0082c8, #667eea, #764ba2, #2193b0)",
        "Sunset Vibes": "linear-gradient(-45deg, #ff6e7f, #bfe9ff, #ff9a9e, #fecfef, #ff6e7f, #ff8a00)",
        "Forest Calm": "linear-gradient(-45deg, #0ba360, #3cba92, #30cfd0, #00b09b, #96c93d, #0ba360)",
        "Aurora": "linear-gradient(-45deg, #7028e4, #e5b2ca, #00c9ff, #92fe9d, #7028e4, #ff6a00)"
    }
    selected_gradient = themes[theme]
    
    st.markdown(f"""
    <style>
    .stApp {{
        background: {selected_gradient} !important;
        background-size: 400% 400% !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Safety Settings")
    show_disclaimer = st.checkbox("Show safety reminder with each answer", value=True)
    
    st.divider()
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.input_tokens = 0
        st.session_state.output_tokens = 0
        st.session_state.total_tokens = 0
        st.rerun()

## Step 8: Create LLM connection
llm = ChatGroq(
    api_key=groq_api_key,
    model=model_id,
    temperature=temperature,
    max_tokens=max_tokens
)

## Step 9: Metrics row
user_messages = sum(1 for m in st.session_state.messages if m["role"] == "user")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Questions Asked", user_messages)
with col2:
    st.metric("Messages Saved", len(st.session_state.messages))
with col3:
    st.metric("Focus", assistant_mode.split("&")[0].strip()[:12])
with col4:
    st.metric("Total Tokens", st.session_state.total_tokens)

## Step 10: Starter prompts - health specific
st.subheader("✨ Try a starter question")
starter_prompt = None
p1, p2, p3, p4 = st.columns(4)

with p1:
    if st.button("🥗 Healthy Diet Tips", use_container_width=True):
        starter_prompt = "What are 5 simple principles of a balanced healthy diet for adults? Explain in simple language."
with p2:
    if st.button("😴 Better Sleep", use_container_width=True):
        starter_prompt = "Give me practical, evidence-based tips to improve sleep quality."
with p3:
    if st.button("🏃 Daily Exercise", use_container_width=True):
        starter_prompt = "What is a simple 20-minute daily exercise routine for a beginner with no equipment?"
with p4:
    if st.button("🩹 First Aid Basics", use_container_width=True):
        starter_prompt = "Explain basic first aid steps for a minor cut or burn at home. Include when to seek medical help."

st.divider()

## Step 11: Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "usage" in message:
            usage = message["usage"]
            st.caption(
                f"Tokens: {usage['input_tokens']} in + {usage['output_tokens']} out = {usage['total_tokens']} total"
            )

## Step 12: System prompt builder - Health safe
def get_system_prompt(mode, lang, safety_reminder):
    base = (
        "You are HealthBot, a friendly, educational health information assistant created for Analytix Camp. "
        "Your role is to provide general health education, wellness information, and healthy lifestyle guidance. "
        "Rules you must follow: "
        "1. You do NOT diagnose conditions or prescribe medications. If user asks for diagnosis, explain possibilities generally and advise to see a clinician. "
        "2. Keep explanations simple, accurate, and supportive. Use short examples when helpful. "
        "3. If unsure, say you are unsure instead of inventing facts. "
        "4. For serious, severe, worsening, or red-flag symptoms (like chest pain, difficulty breathing, high fever, severe injury, thoughts of self-harm), advise urgent professional care. "
        "5. Always encourage consulting a qualified healthcare professional for personal decisions. "
        "6. Do not ask for sensitive personal data like exact location or ID. "
    )
    
    mode_instruction = {
        "General Wellness & Education": "Focus on general wellness, prevention, and healthy habits.",
        "Nutrition & Healthy Eating": "Focus on balanced nutrition principles, portion guidance, and healthy cooking ideas. Avoid extreme diets.",
        "Fitness & Exercise Guidance": "Focus on safe exercise principles, warm-up, progression, and recovery. Tailor to beginner level unless stated otherwise.",
        "Sleep & Stress Management": "Focus on sleep hygiene, stress management techniques, breathing, and daily routine.",
        "First Aid Information": "Provide general first aid information steps and clearly state when to seek emergency help.",
        "Child Health Education": "Provide general child health education for parents. Emphasize pediatrician consultation for any concerns.",
        "Women's Health Education": "Provide general women's health education respectfully and encourage clinician consultation."
    }
    
    lang_instruction = {
        "English": "Answer in clear English.",
        "Urdu (Roman)": "Answer in Roman Urdu (Urdu written in English letters) so it is easy to read locally.",
        "Urdu + English Mix": "Answer in a mix of Roman Urdu and simple English, friendly for Pakistan audience."
    }
    
    safety = ""
    if safety_reminder:
        safety = " At the end of each health-related answer, add a short line: 'This is for education only, please consult a healthcare professional for personal advice.'"
    
    return base + " " + mode_instruction.get(mode, "") + " " + lang_instruction.get(lang, "") + safety

## Step 13: Chat input handling
typed_prompt = st.chat_input("Ask about health, nutrition, fitness, sleep...")
user_prompt = starter_prompt or typed_prompt

if user_prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Build LangChain messages
    langchain_messages = [
        SystemMessage(content=get_system_prompt(assistant_mode, language_pref, show_disclaimer))
    ]
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        else:
            langchain_messages.append(AIMessage(content=msg["content"]))

    # Get AI answer
    with st.chat_message("assistant"):
        # Lottie thinking animation placeholder
        thinking_placeholder = st.empty()
        with thinking_placeholder:
            if st.session_state.lotties.get("thinking"):
                col_t1, col_t2, col_t3 = st.columns([1,1,1])
                with col_t2:
                    lottie_player(st.session_state.lotties["thinking"], height=100, width=100, key=f"thinking_{len(st.session_state.messages)}")
            else:
                st.markdown("🩺 HealthBot is thinking...")
        
        try:
            response = llm.invoke(langchain_messages)
            answer = response.content
            usage = response.usage_metadata or {}
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)

            st.session_state.input_tokens += input_tokens
            st.session_state.output_tokens += output_tokens
            st.session_state.total_tokens += total_tokens

            thinking_placeholder.empty()
            st.markdown(answer)
            st.caption(
                f"Tokens: {input_tokens} in + {output_tokens} out = {total_tokens} total"
            )
            # Success mini animation
            if st.session_state.lotties.get("success"):
                lottie_player(st.session_state.lotties["success"], height=80, width=80, key=f"success_{len(st.session_state.messages)}", loop=False)
                
        except Exception as error:
            thinking_placeholder.empty()
            st.error("Sorry, I could not get a response. Please check your API key or internet.")
            st.exception(error)
            answer = ""
            input_tokens = output_tokens = total_tokens = 0

    # Save assistant answer
    if answer:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                },
            }
        )
        st.rerun()

## Step 14: How it works
with st.expander("ℹ️ How does this HealthBot work?"):
    if st.session_state.lotties.get("medicine"):
        col_a, col_b, col_c = st.columns([1,1,1])
        with col_b:
            lottie_player(st.session_state.lotties["medicine"], height=120, width=120, key="exp_medicine")
    
    st.markdown("""
    **Architecture:**
    1.  **UI:** Streamlit chat interface with Lottie animations
    2.  **Memory:** Streamlit session_state stores conversation
    3.  **LLM:** Groq Cloud running open-source GPT-OSS models via LangChain
    4.  **Safety:** Custom system prompt that prevents diagnosis/prescription and encourages professional consultation
    5.  **Animations:** Lottie JSON animations loaded from LottieFiles CDN with animated gradient background
    
    **To customize further:**
    - Add RAG: Connect your own health PDFs (like nutrition guidelines) using Chroma or FAISS
    - Add user profiles: age range, activity level for more personalized wellness tips
    - Add multilingual: Full Urdu script support
    
    **Files needed:**
    - `.env` file with `GROQ_API_KEY=your_key`
    - `requirements.txt`: 
      ```
      streamlit
      python-dotenv
      langchain-core
      langchain-groq
      requests
      streamlit-lottie (optional, we use direct HTML)
      ```
    """)
    st.caption("Analytix Camp | HealthBot Project | For educational use only | Lottie Edition 🌈💓")
