# Streamlit Configuration for Cloud Deployment

# This file tells Streamlit Cloud to call the API functions directly
# instead of using HTTP requests to localhost

import streamlit as st
from datetime import datetime, date
import pandas as pd
import os

# Set API keys from Streamlit secrets before importing
if hasattr(st, 'secrets'):
    try:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    except Exception as e:
        st.error(f"⚠️ Missing API keys in secrets: {e}")
        st.stop()

# Import directly from the RAG system (no API needed)
import sap_invoice_rag
from sap_invoice_rag import (
    query_invoices,
    get_invoice_count,
    get_invoices_by_date_range
)

# Initialize services with Streamlit secrets
if hasattr(st, 'secrets'):
    try:
        sap_invoice_rag.initialize_services(
            openai_key=st.secrets["OPENAI_API_KEY"],
            pinecone_key=st.secrets["PINECONE_API_KEY"]
        )
    except Exception as e:
        st.error(f"⚠️ Failed to initialize services: {e}")
        st.stop()

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
    
    st.success("✅ Direct Integration")
    
    st.markdown("---")
    
    # Get total invoice count
    st.subheader("📈 Statistics")
    if st.button("Refresh Stats"):
        try:
            count = get_invoice_count()
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
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
    
    # Chat input - Press Enter to send
    user_question = st.chat_input("💬 Type your question and press Enter...")
    
    # Process query when user submits
    if user_question:
        # Add user message to history first
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Get assistant response
        with st.spinner("🤔 Thinking..."):
            try:
                answer = query_invoices(user_question, st.session_state.session_id)
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })
        
        # Rerun to display new messages
        st.rerun()

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
                # Call RAG function directly
                invoices = get_invoices_by_date_range(
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                
                # Store in session state to preserve across reruns
                st.session_state.last_search_results = invoices
                st.session_state.last_search_dates = (start_date, end_date)
                    
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display results from session state
    if 'last_search_results' in st.session_state and st.session_state.last_search_results:
        invoices = st.session_state.last_search_results
        count = len(invoices)
        
        # Display results
        st.success(f"Found {count} invoices")
        
        # Convert to DataFrame
        df = pd.DataFrame(invoices)
        
        # Show what columns we have
        st.info(f"Available columns: {', '.join(df.columns.tolist())}")
        
        # Select relevant columns for display
        display_cols = [
            'invoiceNumber', 'companyCode', 'fiscalYear',
            'documentDateConverted', 'amount', 'currency',
            'documentType', 'postingDateConverted', 'reference'
        ]
        
        # Filter columns that exist
        available_cols = [col for col in display_cols if col in df.columns]
        
        # Display subset of columns
        st.dataframe(
            df[available_cols] if available_cols else df,
            use_container_width=True,
            height=400
        )
        
        # Download button - export ALL columns with all data
        csv = df.to_csv(index=False)
        search_dates = st.session_state.get('last_search_dates', (start_date, end_date))
        st.download_button(
            label=f"📥 Download Full CSV ({len(df)} rows, {len(df.columns)} columns)",
            data=csv,
            file_name=f"invoices_{search_dates[0]}_{search_dates[1]}.csv",
            mime="text/csv",
            key="download_csv"
        )
    elif 'last_search_results' in st.session_state and len(st.session_state.last_search_results) == 0:
        st.warning("No invoices found in this date range.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>SAP Invoice RAG System | Powered by LangChain & OpenAI</div>",
    unsafe_allow_html=True
)
