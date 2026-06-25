import streamlit as st
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from datetime import datetime
import json
import os

st.set_page_config(page_title="AI Categorized Journal", layout="wide")

# --- Environment Configuration ---
# Streamlit will look for this key inside your Advanced Settings -> Secrets panel
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Setup Error: Please configure your GEMINI_API_KEY inside the Streamlit Secrets panel.")
    st.stop()

# Initialize the Native Google GenAI Client
client = genai.Client(api_key=api_key)

# --- 1. Structured AI Schema Definition ---
class AIAnalysis(BaseModel):
    mood: str = Field(description="The primary emotion of the text (e.g., Anxious, Motivated, Content, Exhausted)")
    sentiment: str = Field(description="Overall sentiment: Positive, Negative, or Neutral")
    summary: str = Field(description="A clean, single-sentence summary of the user's thoughts")
    tags: list[str] = Field(description="3 to 5 lowercase topic keywords extracted from the text")

# Initialize an online session memory runtime to handle multi-category CRUD state logs
if "journal_db" not in st.session_state:
    st.session_state.journal_db = []

# --- UI Header Component ---
st.title("📝 Modern Categorized AI Journal Platform")
st.caption("Evolving your categorized text files (Work, Personal, Fitness) into interactive AI dashboards for free using Google Gemini.")

# Structuring application tabs
tab_create, tab_view, tab_update, tab_chat = st.tabs([
    "✍️ Add New Log", 
    "🔍 Review Logs", 
    "✏️ Update / Delete Logs",
    "💬 Reflective Dialogue"
])


# --- TAB 1: CREATE OPERATION ---
with tab_create:
    st.subheader("Document a New Entry")
    
    category = st.selectbox("Select Journal Category:", ["Work", "Personal", "Fitness", "General"])
    user_input = st.text_area("Write your entry content below:", height=150, placeholder="Type your thoughts here...", key="create_box")
    
    if st.button("Process & Save Log"):
        if not user_input.strip():
            st.warning("Journal entry text content cannot be blank.")
        else:
            with st.spinner("Invoking Gemini semantic analysis engines..."):
                try:
                    # Request strict JSON structured analysis from Gemini 1.5 Flash
                    completion = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=user_input,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=AIAnalysis,
                            system_instruction="You are a professional behavioral analytics engine. Analyze the provided journal text to extract emotional trends and summaries accurately."
                        ),
                    )
                    
                    # Parse output string back to JSON dictionary matching Pydantic fields
                    ai_insights = json.loads(completion.text)
                    
                    unique_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
                    
                    document = {
                        "id": unique_id,
                        "timestamp": datetime.utcnow().strftime('%H:%M'),
                        "date_string": datetime.utcnow().strftime("%Y-%m-%d"),
                        "category": category.lower(),
                        "raw_entry": f"[{datetime.utcnow().strftime('%H:%M')}] - {user_input}",
                        "ai_analysis": ai_insights
                    }
                    st.session_state.journal_db.insert(0, document)
                    
                    st.success(f"Journal entry successfully mapped into category: '{category}'!")
                    
                    m_col1, m_col2 = st.columns(2)
                    m_col1.metric("Evaluated Mood Profile", ai_insights["mood"])
                    m_col2.metric("Sentiment Polarity", ai_insights["sentiment"])
                    st.info(f"**AI Automated Summary:** {ai_insights['summary']}")
                    
                except Exception as e:
                    st.error(f"Error communicating with Gemini cloud framework: {str(e)}")


# --- TAB 2: READ OPERATION ---
with tab_view:
    st.subheader("Review Structured Logs")
    search_cat = st.selectbox("Filter logs by category selection (or select 'All'):", ["All", "Work", "Personal", "Fitness", "General"])
    
    matched_entries = st.session_state.journal_db
    if search_cat != "All":
        matched_entries = [item for item in st.session_state.journal_db if item["category"] == search_cat.lower()]
        
    if not matched_entries:
        st.warning(f"No journal entries found matching criteria.")
    else:
        for item in matched_entries:
            with st.container():
                st.markdown(f"### 📅 {item['date_string']} | **Category: {item['category'].upper()}** | *Mood: {item['ai_analysis']['mood']}*")
                st.write(item["raw_entry"])
                st.caption(f"**AI Executive Summary:** {item['ai_analysis']['summary']}")
                st.markdown("---")


# --- TAB 3: UPDATE & DELETE OPERATIONS ---
with tab_update:
    st.subheader("Manage Existing Categorized Entries")
    
    if not st.session_state.journal_db:
        st.warning("No entries available inside repository storage namespaces.")
    else:
        log_options = {
            f"[{entry['category'].upper()}] {entry['date_string']} - {entry['ai_analysis']['summary'][:40]}...": entry['id']
            for entry in st.session_state.journal_db
        }
        
        selected_log_title = st.selectbox("Select entry index target to manipulate:", list(log_options.keys()))
        selected_id = log_options[selected_log_title]
        
        target_index = next(i for i, entry in enumerate(st.session_state.journal_db) if entry['id'] == selected_id)
        target_log = st.session_state.journal_db[target_index]
        
        st.markdown("### Update Configurations")
        update_mode = st.radio("Choose Update Behavior Mode:", ["Append context note to this entry", "Overwrite / Rewrite entry completely"])
        
        # Clean the prefix tag when loading text to update
        clean_text = target_log["raw_entry"].split("] - ", 1)[-1] if "] - " in target_log["raw_entry"] else target_log["raw_entry"]
        new_text_input = st.text_area("Input context string data payload:", value=clean_text, height=100)
        
        col_up, col_del = st.columns(2)
        
        # 1. Update Core Execution
        if col_up.button("✏️ Execute Analytics Update", use_container_width=True):
            if not new_text_input.strip():
                st.error("Input text cannot be blank during updates.")
            else:
                with st.spinner("Gemini is re-indexing modified data schemas..."):
                    try:
                        timestamp = datetime.utcnow().strftime('%H:%M')
                        
                        if "Append" in update_mode:
                            updated_raw = target_log["raw_entry"] + f"\n[{timestamp}] (Updated Component) - {new_text_input}"
                        else:
                            updated_raw = f"[{timestamp}] - {new_text_input}"
                            
                        # Re-run Gemini on modified entry string
                        completion = client.models.generate_content(
                            model='gemini-1.5-flash',
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
                        
                        st.success("Log updated and tracking analytics metadata updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Processing structural updates failed: {e}")
                        
        # 2. Delete Execution
        if col_del.button("🗑️ Delete Selected Log Permanently", use_container_width=True):
            st.session_state.journal_db.pop(target_index)
            st.success("Target item dropped from database arrays.")
            st.rerun()


# --- TAB 4: REFLECTIVE CHAT FRAMEWORK ---
with tab_chat:
    st.subheader("Contextual Reflection Engine")
    chat_prompt = st.text_input("Express what's on your mind right now or ask questions regarding your patterns:")
    
    if st.button("Consult AI Coach") and chat_prompt.strip():
        with st.spinner("Analyzing log tracking trends..."):
            
            past_logs = st.session_state.journal_db[:5]
            history_context = ""
            for entry in reversed(past_logs):
                history_context += f"Category: {entry['category'].upper()} | Mood Profile: {entry['ai_analysis']['mood']}\nContent: {entry['raw_entry']}\n\n"
                
            system_prompt = (
                "You are an empathetic, highly reflective AI journal companion. Your function is to offer encouraging, "
                "insightful, and highly contextual feedback on the user's message using their recent categorised history context.\n\n"
                f"User's Recent Categorized Journal Entries:\n{history_context}"
            )
            
            try:
                # Dispatch conversational payload directly into Gemini Flash
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=chat_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    )
                )
                st.markdown(f"**AI Reflection Coach:**\n\n{response.text}")
            except Exception as e:
                st.error(f"Error compiling response loops: {e}")
