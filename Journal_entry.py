import streamlit as st
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from datetime import datetime
import json
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="MindVault // AI Categorized Journal", 
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Environment Configuration ---
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ **Setup Error:** Please configure your `GEMINI_API_KEY` inside the Streamlit Secrets panel.")
    st.stop()

# Initialize Native Google GenAI Client
client = genai.Client(api_key=api_key)
TARGET_MODEL = 'gemini-2.5-flash'

# --- Structured AI Schema Definition ---
class AIAnalysis(BaseModel):
    mood: str = Field(description="The primary emotion of the text (e.g., Anxious, Motivated, Content, Exhausted)")
    sentiment: str = Field(description="Overall sentiment: Positive, Negative, or Neutral")
    summary: str = Field(description="A clean, single-sentence summary of the user's thoughts")
    tags: list[str] = Field(description="3 to 5 lowercase topic keywords extracted from the text")

# --- Session State Initialization ---
if "journal_db" not in st.session_state:
    st.session_state.journal_db = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Dashboard Metrics ---
with st.sidebar:
    st.title("📊 Journal Analytics")
    st.markdown("Real-time telemetry from your structured entries.")
    
    total_logs = len(st.session_state.journal_db)
    st.metric(label="Total Saved Entries", value=total_logs)
    
    if total_logs > 0:
        categories = [item["category"].capitalize() for item in st.session_state.journal_db]
        dominant_cat = max(set(categories), key=categories.count)
        st.metric(label="Primary Focus Area", value=dominant_cat)
        
        sentiments = [item["ai_analysis"]["sentiment"] for item in st.session_state.journal_db]
        pos_pct = int((sentiments.count("Positive") / len(sentiments)) * 100) if sentiments else 0
        st.metric(label="Positive Sentiment Bias", value=f"{pos_pct}%")
    else:
        st.info("Awaiting structural entries to populate analytical pipelines.")
    
    st.markdown("---")
    st.caption("Powered by **Gemini 2.5 Flash** Architecture.")

# --- Application Header ---
st.title("📝 MindVault: Advanced AI Journal Platform")
st.markdown(
    "Transform unstructured daily thoughts into structured, searchable analytical records "
    "categorized via semantic multi-tier frameworks."
)
st.markdown("---")

# Structuring enhanced application tabs
tab_create, tab_view, tab_update, tab_chat = st.tabs([
    "✍️ Document Entry", 
    "🔍 Analysis Dashboard", 
    "✏️ Index Management",
    "💬 Reflective Dialogue"
])

# --- TAB 1: CREATE OPERATION ---
with tab_create:
    st.markdown("### ✍️ Document a New Entry")
    
    col_input, col_meta = st.columns([3, 1])
    
    with col_meta:
        category = st.selectbox("Assign Category Axis:", ["Personal", "Work", "Fitness", "General"])
        st.caption("Categorization targets downstream filtering logic and context builds.")
        
    with col_input:
        user_input = st.text_area(
            "Write your entry content below:", 
            height=180, 
            placeholder="Type your stream of consciousness or structured logs here...", 
            key="create_box"
        )
    
    if st.button("🚀 Process & Save Log", use_container_width=True):
        if not user_input.strip():
            st.warning("⚠️ Journal entry text content cannot be blank.")
        else:
            with st.spinner("Invoking Gemini semantic analysis engines..."):
                try:
                    completion = client.models.generate_content(
                        model=TARGET_MODEL,
                        contents=user_input,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=AIAnalysis,
                            system_instruction="You are a professional behavioral analytics engine. Analyze the provided journal text to extract emotional trends and summaries accurately."
                        ),
                    )
                    
                    ai_insights = json.loads(completion.text)
                    unique_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
                    
                    document = {
                        "id": unique_id,
                        "timestamp": datetime.utcnow().strftime('%H:%M'),
                        "date_string": datetime.utcnow().strftime("%Y-%m-%d"),
                        "category": category.lower(),
                        "raw_entry": user_input,
                        "ai_analysis": ai_insights
                    }
                    st.session_state.journal_db.insert(0, document)
                    
                    st.success(f"✔️ Journal entry successfully mapped into category: **{category}**!")
                    
                    # Highlight Insights Panel
                    with st.container(border=True):
                        st.markdown("#### 🧠 Extracted Structural Insights")
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("Evaluated Mood Profile", ai_insights["mood"])
                        m_col2.metric("Sentiment Polarity", ai_insights["sentiment"])
                        m_col3.markdown(f"**Tags:** \n" + " ".join([f"`{t}`" for t in ai_insights["tags"]]))
                        
                        st.info(f"**AI Automated Summary:** {ai_insights['summary']}")
                        
                except Exception as e:
                    st.error(f"Error communicating with Gemini cloud framework: {str(e)}")

# --- TAB 2: READ OPERATION ---
with tab_view:
    st.markdown("### 🔍 Historical Analysis Dashboard")
    
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        search_cat = st.selectbox("Filter by Category:", ["All", "Personal", "Work", "Fitness", "General"])
    with col_f2:
        search_query = st.text_input("Search terms inside records:", placeholder="Type to filter content...")
        
    matched_entries = st.session_state.journal_db
    if search_cat != "All":
        matched_entries = [item for item in matched_entries if item["category"] == search_cat.lower()]
    if search_query.strip():
        matched_entries = [item for item in matched_entries if search_query.lower() in item["raw_entry"].lower()]
        
    if not matched_entries:
        st.warning("No records matched your specific filter configurations.")
    else:
        for item in matched_entries:
            with st.container(border=True):
                # Header Badge Meta Line
                st.markdown(
                    f"📅 **{item['date_string']}** @ {item['timestamp']} | "
                    f"🏷️ `{item['category'].upper()}` | "
                    f"🎭 Mood: **{item['ai_analysis']['mood']}** | "
                    f"📈 Sentiment: *{item['ai_analysis']['sentiment']}*"
                )
                st.write(item["raw_entry"])
                st.caption(f"🤖 **Executive Summary:** {item['ai_analysis']['summary']}")
                
                # Render metadata tags
                if "tags" in item["ai_analysis"]:
                    st.markdown(" ".join([f"`#{t}`" for t in item["ai_analysis"]["tags"]]))

# --- TAB 3: UPDATE & DELETE OPERATIONS ---
with tab_update:
    st.markdown("### ✏️ Index Management & System Rescheduling")
    
    if not st.session_state.journal_db:
        st.warning("No entries available inside repository storage namespaces.")
    else:
        log_options = {
            f"[{entry['category'].upper()}] {entry['date_string']} - {entry['ai_analysis']['summary'][:50]}...": entry['id']
            for entry in st.session_state.journal_db
        }
        
        selected_log_title = st.selectbox("Select Target Registry Element:", list(log_options.keys()))
        selected_id = log_options[selected_log_title]
        
        target_index = next((i for i, entry in enumerate(st.session_state.journal_db) if entry['id'] == selected_id), None)
        
        if target_index is not None:
            target_log = st.session_state.journal_db[target_index]
            
            st.markdown("#### Edit Operations Configurator")
            update_mode = st.radio(
                "Execution Stratagem:", 
                ["Append context note to this entry", "Overwrite / Rewrite entry completely"],
                horizontal=True
            )
            
            clean_text = target_log["raw_entry"]
            new_text_input = st.text_area(
                "Modify Text Payload Structure:", 
                value=clean_text, 
                height=150, 
                key=f"update_text_{selected_id}"
            )
            
            col_up, col_del = st.columns(2)
            
            # Update Logic Execution
            if col_up.button("✏️ Execute Analytics Update", use_container_width=True, type="primary"):
                if not new_text_input.strip():
                    st.error("Input text cannot be blank during updates.")
                else:
                    with st.spinner("Gemini is re-indexing modified data schemas..."):
                        try:
                            timestamp = datetime.utcnow().strftime('%H:%M')
                            if "Append" in update_mode:
                                updated_raw = target_log["raw_entry"] + f"\n\n[{timestamp} Update] {new_text_input}"
                            else:
                                updated_raw = new_text_input
                                
                            completion = client.models.generate_content(
                                model=TARGET_MODEL,
                                contents=updated_raw,
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    response_schema=AIAnalysis,
                                    system_instruction="You are a professional behavioral analytics engine. Analyze the provided journal text to extract emotional trends and summaries accurately."
                                ),
                            )
                            new_insights = json.loads(completion.text)
                            
                            st.session_state.journal_db[target_index]["raw_entry"] = updated_raw
                            st.session_state.journal_db[target_index]["ai_analysis"] = new_insights
                            
                            st.success("Log updated and structured analytics re-cached successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Processing structural updates failed: {e}")
                            
            # Delete Logic Execution
            if col_del.button("🗑️ Delete Selected Log Permanently", use_container_width=True):
                st.session_state.journal_db.pop(target_index)
                st.success("Target element purged from local memory state.")
                st.rerun()

# --- TAB 4: REFLECTIVE CHAT FRAMEWORK ---
with tab_chat:
    st.markdown("### 💬 Contextual Reflection Engine")
    st.caption("Engage with an AI companion configured with context windows pointing to your current database matrix.")
    
    if not st.session_state.journal_db:
        st.info("💡 Write a few journal entries first to provide historical context for the dialogue framework.")
    else:
        # Render clean, native conversation streams
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Accept immediate input via modern UI components
        if chat_prompt := st.chat_input("Ask patterns regarding your focus spaces..."):
            with st.chat_message("user"):
                st.markdown(chat_prompt)
            st.session_state.chat_history.append({"role": "user", "content": chat_prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing historical matrix records..."):
                    try:
                        # Extract the top 5 most recent records for prompt engineering injection
                        past_logs = st.session_state.journal_db[:5]
                        history_context = ""
                        for entry in reversed(past_logs):
                            history_context += f"Category: {entry['category'].upper()} | Mood Profile: {entry['ai_analysis']['mood']}\nContent: {entry['raw_entry']}\n\n"
                            
                        system_prompt = (
                            "You are an empathetic, highly reflective AI journal companion. Your function is to offer encouraging, "
                            "insightful, and highly contextual feedback on the user's message using their recent categorised history context.\n\n"
                            f"User's Recent Categorized Journal Entries:\n{history_context}"
                        )
                        
                        response = client.models.generate_content(
                            model=TARGET_MODEL,
                            contents=chat_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_prompt
                            )
                        )
                        
                        st.markdown(response.text)
                        st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Error compiling response loops: {e}")
