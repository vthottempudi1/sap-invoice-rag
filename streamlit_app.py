"""
Streamlit App for SAP Invoice RAG System
"""

import streamlit as st
import requests
from datetime import datetime, date
import pandas as pd

# API Configuration
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="SAP Invoice Assistant",
    page_icon="📊",
    layout="wide"
)

# Session state initialization
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stats-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📊 SAP Invoice Assistant</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check API health
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Not Running")
        st.info("Start API: `python api_server.py`")
    
    st.markdown("---")
    
    # Get total invoice count
    st.subheader("📈 Statistics")
    if st.button("Refresh Stats"):
        try:
            response = requests.get(f"{API_URL}/count")
            if response.status_code == 200:
                count = response.json()["total_count"]
                st.metric("Total Invoices", count)
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Session info
    st.subheader("🔑 Session Info")
    st.text_input("Session ID", value=st.session_state.session_id, disabled=True)
    
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    
    # Example queries
    st.subheader("💡 Example Queries")
    st.markdown("""
    - How many invoices in 2024?
    - Show invoices with company code MF01
    - What are the document types?
    - Invoices from 2025?
    - Show me invoice 5100000000
    """)

# Main content area with tabs
tab1, tab2 = st.tabs(["💬 Chat Assistant", "📅 Date Range Query"])

# Tab 1: Chat Assistant
with tab1:
    st.subheader("Ask questions about your invoices")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><b>Assistant:</b> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_question = st.text_input(
            "Type your question here...",
            key="question_input",
            placeholder="e.g., How many invoices do we have?"
        )
    
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    # Process query
    if send_button and user_question:
        with st.spinner("🤔 Thinking..."):
            try:
                # Send to API
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "question": user_question,
                        "session_id": st.session_state.session_id
                    }
                )
                
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_question
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                    
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Error: {e}")

# Tab 2: Date Range Query
with tab2:
    st.subheader("Query invoices by date range")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date(2024, 1, 1)
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=date(2024, 12, 31)
        )
    
    if st.button("Search by Date Range", type="primary"):
        with st.spinner("Searching..."):
            try:
                response = requests.post(
                    f"{API_URL}/invoices/date-range",
                    json={
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d")
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    count = data["count"]
                    invoices = data["invoices"]
                    
                    # Display results
                    st.success(f"Found {count} invoices")
                    
                    if count > 0:
                        # Convert to DataFrame
                        df = pd.DataFrame(invoices)
                        
                        # Select relevant columns
                        display_cols = [
                            'invoiceNumber', 'companyCode', 'fiscalYear',
                            'documentDateConverted', 'amount', 'currency',
                            'documentType'
                        ]
                        
                        # Filter columns that exist
                        available_cols = [col for col in display_cols if col in df.columns]
                        
                        st.dataframe(
                            df[available_cols],
                            use_container_width=True,
                            height=400
                        )
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"invoices_{start_date}_{end_date}.csv",
                            mime="text/csv"
                        )
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>SAP Invoice RAG System | Powered by LangChain & OpenAI</div>",
    unsafe_allow_html=True
)
