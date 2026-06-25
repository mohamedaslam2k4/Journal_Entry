import streamlit as st
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from datetime import datetime
import json
import os
import pandas as pd

# --- Advanced Page & Theme Configuration ---
st.set_page_config(
    page_title="MindVault Premium // AI Analytics Journal", 
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Injector for modern UI polish (Neomorphic hints, clean borders, custom badges)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        gap: 4px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-bottom: 2px solid #FF4B4B !important;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- Environment Verification ---
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ **System Initialization Failure:** `GEMINI_API_KEY` missing from environment schemas.")
    st.stop()

# Client Registry
client = genai.Client(api_key=api_key)
TARGET_MODEL = 'gemini-2.5-flash'

# --- Structured Pydantic Semantic Schema ---
class AIAnalysis(BaseModel):
    mood: str = Field(description="The primary emotion of the text (e.g., Anxious, Motivated, Content, Exhausted)")
    sentiment: str = Field(description="Overall sentiment: Positive, Negative, or Neutral")
    summary: str = Field(description="A clean, single-sentence summary of the user's thoughts")
    tags: list[str] = Field(description="3 to 5 lowercase topic keywords extracted from the text")

# --- Persistent Session Core State ---
if "journal_db" not in st.session_state:
    st.session_state.journal_db = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR: SYSTEM TELEMETRY & DATA PORTABILITY ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/journal.png", width=70)
    st.title("MindVault Telemetry")
    st.caption("Engine State: Active // Free Tier")
    st.markdown("---")
    
    # Live KPI Control Matrix
    total_logs = len(st.session_state.journal_db)
    st.metric(label="Total Index Volume", value=total_logs, delta=f"+{total_logs} nodes" if total_logs else None)
    
    if total_logs > 0:
        categories = [item["category"].capitalize() for item in st.session_state.journal_db]
        dominant_cat = max(set(categories), key=categories.count)
        st.metric(label="Core Concentration Cluster", value=dominant_cat)
        
        sentiments = [item["ai_analysis"]["sentiment"] for item in st.session_state.journal_db]
        pos_pct = int((sentiments.count("Positive") / len(sentiments)) * 100) if sentiments else 0
        st.metric(label="Optimism Index Quotient", value=f"{pos_pct}%")
        
        st.markdown("---")
        st.markdown("### 💾 Data Portability Operations")
        
        # Advanced Feature: JSON Export
        json_string = json.dumps(st.session_state.journal_db, indent=4)
        st.download_button(
            label="📤 Export Secure Schema (JSON)",
            file_name=f"mindvault_backup_{datetime.utcnow().strftime('%Y%m%d')}.json",
            mime="application/json",
            data=json_string,
            use_container_width=True
        )
    else:
        st.info("📊 Local data matrix empty. Telemetry metrics offline.")
        
    st.markdown("---")
    # Backup restore sub-utility
    uploaded_file = st.file_uploader("📥 Restore Database Instance", type=["json"])
    if uploaded_file is not None:
        try:
            st.session_state.journal_db = json.load(uploaded_file)
            st.success("Database instance restored successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Restoration parsing failure: {e}")

# --- MAIN APP GRID ARCHITECTURE ---
st.title("🧠 MindVault Premium: Cognitive Analytical Ledger")
st.markdown("An advanced AI analytical orchestration matrix that structures cognitive streams into semantic vector spaces using real-time LLM validation.")

# Modernized UI Layout Tab Blocks
tab_create, tab_view, tab_update, tab_chat = st.tabs([
    "✍️ Stream Ingestion Engine", 
    "🔮 Vector Dashboard & Matrix", 
    "⚙️ Registry Index Tuning",
    "🤖 Deep Reflective Co-Pilot"
])

# --- TAB 1: ADVANCED CREATE OPERATION ---
with tab_create:
    st.markdown("### ✍️ Document Entry Vector")
    
    col_input, col_meta = st.columns([3, 1])
    
    with col_meta:
        category = st.selectbox("Strategic Dimension Axis:", ["Personal", "Work", "Fitness", "General", "Financial", "Crisis"])
        priority = st.select_slider("Subjective Impact Matrix Scale:", options=["Low", "Medium", "High", "Critical"])
        st.caption("Funnels downstream priority queuing in the reflection subsystem.")
        
    with col_input:
        user_input = st.text_area(
            "Ingest consciousness raw text content stream:", 
            height=200, 
            placeholder="Document situational logs, project roadblocks, existential breakdowns, or metric configurations...", 
            key="create_box"
        )
    
    if st.button("⚡ Ingest, Analyze & Pipeline Object", use_container_width=True, type="primary"):
        if not user_input.strip():
            st.warning("⚠️ Ingestion Pipeline Rejected: Text content empty.")
        else:
            with st.status("Initializing Multi-Tier Cognitive Pipeline Analysis...", expanded=True) as status:
                try:
                    status.write("🧠 Contacting Google Gemini 2.5 Inference Fabrics...")
                    completion = client.models.generate_content(
                        model=TARGET_MODEL,
                        contents=user_input,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=AIAnalysis,
                            system_instruction="You are an enterprise psychological behavioral analytics engine. Extract emotional matrix points, clean crisp single-line executive high-level summaries, and structural tags."
                        ),
                    )
                    
                    status.write("🧮 Formatting structured JSON payload schema architecture...")
                    ai_insights = json.loads(completion.text)
                    unique_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
                    
                    document = {
                        "id": unique_id,
                        "timestamp": datetime.utcnow().strftime('%H:%M:%S'),
                        "date_string": datetime.utcnow().strftime("%Y-%m-%d"),
                        "category": category.lower(),
                        "priority": priority,
                        "raw_entry": user_input,
                        "ai_analysis": ai_insights
                    }
                    st.session_state.journal_db.insert(0, document)
                    status.update(label="Ingestion Sequence Success! Block saved to memory store.", state="complete")
                    
                    # Real-time Dashboard Flash Card
                    with st.container(border=True):
                        st.markdown("#### 🛠️ Generated Block Telemetry")
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("Mood Structural Metric", ai_insights["mood"])
                        m_col2.metric("Sentiment Polarity Vector", ai_insights["sentiment"])
                        m_col3.markdown("**Computed Node Sub-tags:**\n" + " ".join([f"`#{t}`" for t in ai_insights["tags"]]))
                        st.info(f"💡 **AI Executive Abstract Summary:** {ai_insights['summary']}")
                        
                except Exception as e:
                    status.update(label="Pipeline System Crash", state="error")
                    st.error(f"Inference Exception Block Intercepted: {str(e)}")

# --- TAB 2: ADVANCED VIEW & ANALYTICS OPERATION ---
with tab_view:
    st.markdown("### 🔮 Ledger Matrix Explorer")
    
    # Multi-dimensional UI filter bar
    with st.popover("⚙️ Open Multi-Tier Search Filtering Matrix", use_container_width=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            search_cat = st.selectbox("Category Dimension:", ["All", "Personal", "Work", "Fitness", "General", "Financial", "Crisis"])
        with f_col2:
            search_priority = st.multiselect("Impact Priorities:", ["Low", "Medium", "High", "Critical"], default=["Low", "Medium", "High", "Critical"])
        with f_col3:
            search_sentiment = st.selectbox("Sentiment State:", ["All", "Positive", "Negative", "Neutral"])
            
    search_query = st.text_input("🔍 Dynamic Substring Search Query Matching Layer:", placeholder="Type keywords to query index pools instantly...")
    
    # Filtering Pipeline logic
    matched_entries = st.session_state.journal_db
    if search_cat != "All":
        matched_entries = [item for item in matched_entries if item["category"] == search_cat.lower()]
    if search_sentiment != "All":
        matched_entries = [item for item in matched_entries if item["ai_analysis"]["sentiment"] == search_sentiment]
    matched_entries = [item for item in matched_entries if item.get("priority", "Medium") in search_priority]
    if search_query.strip():
        matched_entries = [item for item in matched_entries if search_query.lower() in item["raw_entry"].lower() or search_query.lower() in item["ai_analysis"]["summary"].lower()]
        
    if not matched_entries:
        st.warning("⚠️ No database nodes matched your current filter criteria parameters.")
    else:
        for item in matched_entries:
            # High premium structural containers for each node
            with st.container(border=True):
                h_col1, h_col2 = st.columns([4, 1])
                with h_col1:
                    st.markdown(
                        f"⚡ **{item['date_string']}** @ {item['timestamp']} | "
                        f"📂 `{item['category'].upper()}` | "
                        f"🚨 Impact Level: **{item.get('priority', 'Medium').upper()}**"
                    )
                with h_col2:
                    sentiment_color = "🟢" if item['ai_analysis']['sentiment'] == "Positive" else "🔴" if item['ai_analysis']['sentiment'] == "Negative" else "🟡"
                    st.markdown(f"{sentiment_color} **{item['ai_analysis']['mood']}**")
                
                st.markdown(f"*{item['ai_analysis']['summary']}*")
                
                with st.expander("📄 View Full Uncompressed Raw Context Payload"):
                    st.code(item["raw_entry"], language="text")
                    
                # Tags rendering layout
                if "tags" in item["ai_analysis"]:
                    st.markdown(" ".join([f"`#{t}`" for t in item["ai_analysis"]["tags"]]))

# --- TAB 3: REGISTRY MANAGEMENT ---
with tab_update:
    st.markdown("### ⚙️ Registry Mutation & Index Shifting Operations")
    
    if not st.session_state.journal_db:
        st.warning("Infrastructure Warning: Memory namespaces empty.")
    else:
        log_options = {
            f"[{entry['category'].upper()}] [{entry.get('priority', 'Medium')}] {entry['date_string']} - {entry['ai_analysis']['summary'][:60]}...": entry['id']
            for entry in st.session_state.journal_db
        }
        
        selected_log_title = st.selectbox("Select Memory Storage Index Block Target:", list(log_options.keys()))
        selected_id = log_options[selected_log_title]
        
        target_index = next((i for i, entry in enumerate(st.session_state.journal_db) if entry['id'] == selected_id), None)
        
        if target_index is not None:
            target_log = st.session_state.journal_db[target_index]
            
            up_col1, up_col2 = st.columns([2, 1])
            with up_col2:
                st.markdown("##### Current Vector Schema")
                st.json(target_log["ai_analysis"])
                
            with up_col1:
                st.markdown("##### Mutate Node State Data")
                update_mode = st.radio(
                    "Mutation Mode Stratagem:", 
                    ["Append timestamped context offset slice", "Destructive overwrite re-compilation"],
                    horizontal=True
                )
                
                new_text_input = st.text_area(
                    "Modify payload context fields:", 
                    value=target_log["raw_entry"], 
                    height=180, 
                    key=f"update_text_{selected_id}"
                )
                
                col_up, col_del = st.columns(2)
                
                if col_up.button("⚙️ Mutate Engine Matrix Logs", use_container_width=True, type="primary"):
                    if not new_text_input.strip():
                        st.error("Operation Denied: Context target block cannot be mutated to blank space strings.")
                    else:
                        with st.spinner("Re-indexing mutated schemas via Gemini system pipelines..."):
                            try:
                                timestamp = datetime.utcnow().strftime('%H:%M:%S')
                                if "Append" in update_mode:
                                    updated_raw = target_log["raw_entry"] + f"\n\n[Mutation Offset Added @ {timestamp} UTC]:\n{new_text_input}"
                                else:
                                    updated_raw = new_text_input
                                    
                                completion = client.models.generate_content(
                                    model=TARGET_MODEL,
                                    contents=updated_raw,
                                    config=types.GenerateContentConfig(
                                        response_mime_type="application/json",
                                        response_schema=AIAnalysis,
                                        system_instruction="Analyze mutated text sequences to update behavioral profiling logs."
                                    ),
                                )
                                new_insights = json.loads(completion.text)
                                
                                st.session_state.journal_db[target_index]["raw_entry"] = updated_raw
                                st.session_state.journal_db[target_index]["ai_analysis"] = new_insights
                                
                                st.success("Matrix node updated and historical pipeline re-cached.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Mutation Failure Sequence Blocked: {e}")
                                
                if col_del.button("🗑️ Destroy Matrix Node Space Permanently", use_container_width=True):
                    st.session_state.journal_db.pop(target_index)
                    st.success("Target context successfully dropped from global dictionary arrays.")
                    st.rerun()

# --- TAB 4: CHAT WITH EXPANDED ARCHITECTURE NATIVE CONTROLS ---
with tab_chat:
    st.markdown("### 🤖 Deep Reflective Co-Pilot Framework")
    st.caption("Active Core Instance Session Linked with Top-tier Node Matrix Data Points.")
    
    if not st.session_state.journal_db:
        st.info("💡 Write a few database index records first to provide proper memory space injection contexts.")
    else:
        # Clear Matrix Interface Control Option
        if st.button("🧼 Purge Current Chat Conversation Buffer", help="Resets agent transient conversation loops."):
            st.session_state.chat_history = []
            st.rerun()
            
        # Native Interactive Chat Stream Modules
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if chat_prompt := st.chat_input("Query structural patterns, behavioral vectors, or long-term trends..."):
            with st.chat_message("user"):
                st.markdown(chat_prompt)
            st.session_state.chat_history.append({"role": "user", "content": chat_prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Processing deep history multi-tier context strings..."):
                    try:
                        # Extract structural historical contexts from latest entries
                        past_logs = st.session_state.journal_db[:8]
                        history_context = ""
                        for entry in reversed(past_logs):
                            history_context += f"Date: {entry['date_string']} | Dimension: {entry['category'].upper()} | Impact: {entry.get('priority', 'Medium')} | Profile: {entry['ai_analysis']['mood']}\nContent Log: {entry['raw_entry']}\nSummary: {entry['ai_analysis']['summary']}\n\n"
                            
                        system_prompt = (
                            "You are MindVault Premium Co-Pilot, an elite, highly reflective AI behavioral analyst and executive coach. "
                            "Provide highly professional, deeply context-aware advice referencing specific patterns from the historical logs provided. "
                            "Be direct, insightful, objective, and deeply encouraging based on factual entries.\n\n"
                            f"User's Historical Context Matrix Streams:\n{history_context}"
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
                        st.error(f"Co-Pilot Runtime Execution Failure: {e}")
