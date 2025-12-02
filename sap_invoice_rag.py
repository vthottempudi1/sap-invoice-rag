"""
SAP Invoice RAG System with Pinecone
Handles invoice retrieval, deduplication, and date filtering
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Set
import re
from collections import defaultdict
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from pinecone import Pinecone

# Load environment variables from .env file (for local development)
load_dotenv()

# Configuration - support both environment variables and direct setting
def get_api_key(key_name: str, default: str = "") -> str:
    """Get API key from environment or return default"""
    return os.getenv(key_name, default)

OPENAI_API_KEY = get_api_key("OPENAI_API_KEY", "your-openai-api-key")
PINECONE_API_KEY = get_api_key("PINECONE_API_KEY", "your-pinecone-api-key")
PINECONE_INDEX = "n8n-s4hana-new"
PINECONE_NAMESPACE = "invoice-documents"

# Global variables for lazy initialization
_pc = None
_embeddings = None
_vectorstore = None
_retriever = None

def initialize_services(openai_key: str = None, pinecone_key: str = None):
    """Initialize services with provided or environment API keys"""
    global _pc, _embeddings, _vectorstore, _retriever, OPENAI_API_KEY, PINECONE_API_KEY
    
    # Use provided keys or fall back to environment/module variables
    if openai_key:
        OPENAI_API_KEY = openai_key
        os.environ["OPENAI_API_KEY"] = openai_key
    if pinecone_key:
        PINECONE_API_KEY = pinecone_key
    
    # Initialize Pinecone
    _pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Initialize embeddings
    _embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=512,
        api_key=OPENAI_API_KEY
    )
    
    # Initialize vector store
    _vectorstore = PineconeVectorStore(
        index_name=PINECONE_INDEX,
        embedding=_embeddings,
        namespace=PINECONE_NAMESPACE,
        pinecone_api_key=PINECONE_API_KEY
    )
    
    return _vectorstore

def get_vectorstore():
    """Get or initialize vectorstore"""
    global _vectorstore
    if _vectorstore is None:
        initialize_services()
    return _vectorstore

# Initialize services on import for backward compatibility
try:
    vectorstore = initialize_services()
except Exception as e:
    print(f"Warning: Could not initialize services on import: {e}")
    vectorstore = None

def get_retriever():
    """Get or create retriever"""
    global _retriever
    if _retriever is None:
        vs = get_vectorstore()
        if vs:
            _retriever = vs.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 100}
            )
    return _retriever

# Create retriever with high k to get all chunks (for backward compatibility)
if vectorstore:
    retriever = vectorstore.as_retriever(
    search_kwargs={"k": 50}
)


def convert_sap_date(sap_date_str: str) -> str:
    """
    Convert SAP date format /Date(timestamp)/ to YYYY-MM-DD
    
    Args:
        sap_date_str: Date string in format /Date(1609113600000)/
        
    Returns:
        Date string in YYYY-MM-DD format or original if conversion fails
    """
    if not sap_date_str or not isinstance(sap_date_str, str):
        return sap_date_str
    
    match = re.search(r'/Date\((\d+)\)/', sap_date_str)
    if match:
        timestamp = int(match.group(1))
        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.strftime('%Y-%m-%d')
    
    return sap_date_str


def deduplicate_invoices(documents: List[Any]) -> List[Dict[str, Any]]:
    """
    Deduplicate invoice documents by invoiceNumber + companyCode + fiscalYear
    
    Args:
        documents: List of LangChain documents from retriever
        
    Returns:
        List of unique invoices with converted dates
    """
    unique_invoices = {}
    
    for doc in documents:
        # Create composite ID from invoice number, company code, and fiscal year
        invoice_num = doc.metadata.get('invoiceNumber', '')
        company_code = doc.metadata.get('companyCode', '')
        fiscal_year = doc.metadata.get('fiscalYear', '')
        
        if not invoice_num:
            continue
        
        # Create unique ID
        invoice_id = f"{invoice_num}_{company_code}_{fiscal_year}"
        
        # If we've already seen this ID, skip
        if invoice_id in unique_invoices:
            continue
        
        # Convert SAP dates
        invoice_data = doc.metadata.copy()
        invoice_data['text'] = doc.page_content
        invoice_data['ID'] = invoice_id
        
        if 'documentDate' in invoice_data:
            invoice_data['documentDateConverted'] = convert_sap_date(invoice_data['documentDate'])
        
        if 'postingDate' in invoice_data:
            invoice_data['postingDateConverted'] = convert_sap_date(invoice_data['postingDate'])
        
        if 'lastChanged' in invoice_data and invoice_data['lastChanged']:
            invoice_data['lastChangedConverted'] = convert_sap_date(invoice_data['lastChanged'])
        
        unique_invoices[invoice_id] = invoice_data
    
    return list(unique_invoices.values())


def filter_by_date_range(invoices: List[Dict], start_date: str = None, end_date: str = None) -> List[Dict]:
    """
    Filter invoices by date range
    
    Args:
        invoices: List of invoice dictionaries
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Filtered list of invoices
    """
    if not start_date or not end_date:
        return invoices
    
    filtered = []
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    for invoice in invoices:
        doc_date_str = invoice.get('documentDateConverted')
        if doc_date_str:
            try:
                doc_date = datetime.strptime(doc_date_str, '%Y-%m-%d')
                if start <= doc_date <= end:
                    filtered.append(invoice)
            except ValueError:
                continue
    
    return filtered


# Custom tool that returns only summarized invoice data
from langchain.tools import tool

@tool
def search_invoice_documents(query: str) -> str:
    """Search SAP invoice documents and return summarized results. Each invoice may appear as multiple chunks - automatically deduplicates by ID field. Use this to find invoices, count totals, or filter by criteria. Returns ALL matching invoices with full details."""
    # Retrieve documents
    ret = get_retriever()
    if not ret:
        return "Error: Retriever not initialized"
    docs = ret.invoke(query)
    
    # Deduplicate by ID
    unique_invoices = deduplicate_invoices(docs)
    
    if not unique_invoices:
        return "No invoices found matching your query."
    
    # Analyze by fiscal year for date-based queries
    invoices_by_year = {}
    for inv in unique_invoices:
        fy = inv.get('fiscalYear', 'Unknown')
        doc_date = inv.get('documentDateConverted', '')
        if fy not in invoices_by_year:
            invoices_by_year[fy] = []
        invoices_by_year[fy].append({'num': inv.get('invoiceNumber'), 'date': doc_date, 'company': inv.get('companyCode')})
    
    # Build result
    result = f"TOTAL: {len(unique_invoices)} unique invoices found.\n\n"
    
    # Show breakdown by fiscal year
    result += "Breakdown by Fiscal Year:\n"
    for fy in sorted(invoices_by_year.keys()):
        result += f"  FY{fy}: {len(invoices_by_year[fy])} invoices\n"
    
    # Show ALL invoices with details (condensed format)
    result += f"\nComplete List of All {len(unique_invoices)} Invoices:\n"
    for i, inv in enumerate(unique_invoices, 1):
        doc_date = inv.get('documentDateConverted', inv.get('documentDate', 'N/A'))
        post_date = inv.get('postingDateConverted', inv.get('postingDate', 'N/A'))
        last_updated = inv.get('lastUpdated', 'N/A')
        reference = inv.get('reference', 'N/A')
        result += f"{i}. #{inv.get('invoiceNumber')} | {inv.get('companyCode')} | FY{inv.get('fiscalYear')} | DocDate:{doc_date} | PostDate:{post_date} | Amt:{inv.get('amount', 0)} {inv.get('currency', 'USD')} | Type:{inv.get('documentType', 'N/A')} | Ref:{reference} | Updated:{last_updated}\n"
    
    # Add summary stats
    company_codes = {}
    doc_types = {}
    for inv in unique_invoices:
        cc = inv.get('companyCode', 'N/A')
        dt = inv.get('documentType', 'N/A')
        company_codes[cc] = company_codes.get(cc, 0) + 1
        doc_types[dt] = doc_types.get(dt, 0) + 1
    
    result += f"\n\nCompany Breakdown: "
    result += ", ".join([f"{cc}({count})" for cc, count in sorted(company_codes.items())])
    result += f"\nDocument Type Breakdown: "
    result += ", ".join([f"{dt}({count})" for dt, count in sorted(doc_types.items())])
    
    return result

# System prompt
system_prompt = """You are an AI assistant that helps users query SAP invoice data from a Pinecone vector database.

CRITICAL RULES:

1. FILTERING BY CRITERIA:
   - When user asks for specific company code, fiscal year, or other filter - COUNT ONLY MATCHING INVOICES
   - Use the "Company Breakdown" and "Document Type Breakdown" sections to get accurate counts
   - Example: If asked "invoices with company code MF01" and breakdown shows "MF01(26)" → Answer is "26 invoices"
   - Example: If asked "invoices with company code ZSYK" and breakdown shows "ZSYK(5)" → Answer is "5 invoices"
   - NEVER use the TOTAL count when user asks for filtered results

2. READING THE COMPLETE LIST:
   - The tool returns "Complete List of All X Invoices" - this shows ALL invoices found
   - Count invoices matching the user's criteria from the complete list OR use the breakdown section
   - Breakdown format: CompanyCode(count) - use this count for accuracy

3. DATE HANDLING:
   - SAP dates are converted to YYYY-MM-DD format
   - For fiscal year queries, use the "Breakdown by Fiscal Year" section
   - Example: "FY2024: 28 invoices" means 28 invoices in fiscal year 2024

4. WORKFLOW:
   - Use search_invoice_documents tool for ANY query
   - Read the breakdown sections carefully
   - When filtering, use breakdown counts or manually count from complete list
   - Provide accurate counts based on user's specific criteria

Never hallucinate data. Always use the breakdown sections for accurate filtered counts."""

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Global variables for agent
_llm = None
_agent = None
_agent_executor = None
_agent_with_chat_history = None

# Chat history management
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def get_agent_with_history():
    """Get or create agent with chat history"""
    global _llm, _agent, _agent_executor, _agent_with_chat_history
    
    if _agent_with_chat_history is None:
        # Initialize LLM
        api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=api_key
        )
        
        # Create agent
        _agent = create_openai_tools_agent(_llm, [search_invoice_documents], prompt)
        
        # Create agent executor
        _agent_executor = AgentExecutor(
            agent=_agent,
            tools=[search_invoice_documents],
            verbose=False,  # Disable verbose output
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        # Wrap agent with message history
        _agent_with_chat_history = RunnableWithMessageHistory(
            _agent_executor,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
    
    return _agent_with_chat_history

# Initialize on import for backward compatibility
try:
    agent_with_chat_history = get_agent_with_history()
except Exception as e:
    print(f"Warning: Could not initialize agent on import: {e}")
    agent_with_chat_history = None


def query_invoices(question: str, session_id: str = "default") -> str:
    """
    Query the SAP invoice system
    
    Args:
        question: User's question about invoices
        session_id: Session ID for chat history
        
    Returns:
        AI's response
    """
    agent = get_agent_with_history()
    if not agent:
        return "Error: Agent not initialized. Please check API keys."
    
    response = agent.invoke(
        {"input": question},
        config={"configurable": {"session_id": session_id}}
    )
    
    return response["output"]


def get_invoice_count() -> int:
    """
    Get total count of unique invoices in the database
    
    Returns:
        Number of unique invoices
    """
    # Query for all invoices
    ret = get_retriever()
    if not ret:
        return 0
    docs = ret.invoke("invoice document financial")
    
    # Deduplicate
    unique_invoices = deduplicate_invoices(docs)
    
    return len(unique_invoices)


def get_invoices_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """
    Get invoices within a date range
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of invoices in the date range
    """
    # Query for all invoices
    ret = get_retriever()
    if not ret:
        return []
    docs = ret.invoke("invoice document financial")
    
    # Deduplicate
    unique_invoices = deduplicate_invoices(docs)
    
    # Filter by date
    filtered = filter_by_date_range(unique_invoices, start_date, end_date)
    
    return filtered


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("SAP Invoice RAG System - Interactive Mode")
    print("=" * 50)
    print("Type your questions or 'quit' to exit")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            response = query_invoices(user_input)
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
