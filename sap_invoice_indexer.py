"""
SAP Invoice Indexing Script
Indexes invoice data from JSON files to Pinecone vector database
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-pinecone-api-key")
PINECONE_INDEX = "n8n-s4hana-new"
PINECONE_NAMESPACE = "invoice-documents"
PINECONE_ENVIRONMENT = "us-east-1"  # Update with your Pinecone environment

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Initialize embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,
    api_key=OPENAI_API_KEY
)


def create_index_if_not_exists():
    """Create Pinecone index if it doesn't exist"""
    try:
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if PINECONE_INDEX not in existing_indexes:
            print(f"Creating index: {PINECONE_INDEX}")
            pc.create_index(
                name=PINECONE_INDEX,
                dimension=512,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=PINECONE_ENVIRONMENT
                )
            )
            print("Index created successfully")
        else:
            print(f"Index '{PINECONE_INDEX}' already exists")
    except Exception as e:
        print(f"Error creating index: {e}")


def load_invoice_data(json_file_path: str) -> List[Dict[str, Any]]:
    """
    Load invoice data from JSON file
    
    Args:
        json_file_path: Path to JSON file containing invoice data
        
    Returns:
        List of invoice dictionaries
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Check for common keys that might contain the invoice list
        for key in ['invoices', 'data', 'results', 'items']:
            if key in data:
                return data[key]
        # If single invoice object
        return [data]
    
    return []


def prepare_documents(invoices: List[Dict[str, Any]]) -> List[Document]:
    """
    Convert invoice data to LangChain Documents with metadata
    
    Args:
        invoices: List of invoice dictionaries
        
    Returns:
        List of LangChain Document objects
    """
    documents = []
    
    for idx, invoice in enumerate(invoices):
        # Extract key fields for text content
        invoice_number = invoice.get('invoiceNumber', invoice.get('DocumentNumber', 'Unknown'))
        company_code = invoice.get('companyCode', invoice.get('CompanyCode', 'Unknown'))
        fiscal_year = invoice.get('fiscalYear', invoice.get('FiscalYear', 'Unknown'))
        amount = invoice.get('amount', invoice.get('Amount', 0))
        currency = invoice.get('currency', invoice.get('Currency', 'USD'))
        document_date = invoice.get('documentDate', invoice.get('DocumentDate', ''))
        posting_date = invoice.get('postingDate', invoice.get('PostingDate', ''))
        document_type = invoice.get('documentType', invoice.get('DocumentType', ''))
        reference = invoice.get('reference', invoice.get('Reference', ''))
        business_area = invoice.get('businessArea', invoice.get('BusinessArea', ''))
        
        # Create text content for embedding
        text_content = f"""Invoice Number: {invoice_number}
Company Code: {company_code}
Fiscal Year: {fiscal_year}
Document Type: {document_type}
Amount: {amount} {currency}
Document Date: {document_date}
Posting Date: {posting_date}
Business Area: {business_area}
Reference: {reference}"""
        
        # Add any additional text fields
        for key, value in invoice.items():
            if isinstance(value, str) and len(value) > 10 and key not in [
                'invoiceNumber', 'companyCode', 'fiscalYear', 'documentDate', 
                'postingDate', 'documentType', 'reference', 'businessArea'
            ]:
                text_content += f"\n{key}: {value}"
        
        # Create unique ID
        invoice_id = f"invoice_{invoice_number}_{company_code}_{fiscal_year}"
        
        # Prepare metadata
        metadata = {
            'ID': invoice_id,
            'invoiceNumber': str(invoice_number),
            'companyCode': str(company_code),
            'fiscalYear': str(fiscal_year),
            'amount': float(amount) if amount else 0,
            'currency': str(currency),
            'documentDate': str(document_date),
            'postingDate': str(posting_date),
            'documentType': str(document_type),
            'reference': str(reference),
            'businessArea': str(business_area),
            'source': 'SAP_S4HANA'
        }
        
        # Add all other fields to metadata (keeping original keys)
        for key, value in invoice.items():
            if key not in metadata and not isinstance(value, (dict, list)):
                metadata[key] = str(value)
        
        # Create Document
        doc = Document(
            page_content=text_content,
            metadata=metadata
        )
        
        documents.append(doc)
    
    return documents


def chunk_documents(documents: List[Document], chunk_size: int = 1000) -> List[Document]:
    """
    Split documents into smaller chunks if needed
    
    Args:
        documents: List of Document objects
        chunk_size: Maximum characters per chunk
        
    Returns:
        List of chunked Document objects
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunked_docs = []
    for doc in documents:
        if len(doc.page_content) > chunk_size:
            # Split into chunks
            chunks = text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                # Create new document with same metadata plus chunk info
                chunk_metadata = doc.metadata.copy()
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                
                chunked_docs.append(Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                ))
        else:
            chunked_docs.append(doc)
    
    return chunked_docs


def index_invoices(json_file_path: str, use_chunking: bool = True):
    """
    Index invoices from JSON file to Pinecone
    
    Args:
        json_file_path: Path to JSON file
        use_chunking: Whether to split large documents into chunks
    """
    print(f"\nIndexing invoices from: {json_file_path}")
    
    # Load invoice data
    print("Loading invoice data...")
    invoices = load_invoice_data(json_file_path)
    print(f"Loaded {len(invoices)} invoices")
    
    if not invoices:
        print("No invoices found in file")
        return
    
    # Prepare documents
    print("Preparing documents...")
    documents = prepare_documents(invoices)
    print(f"Created {len(documents)} documents")
    
    # Chunk documents if needed
    if use_chunking:
        print("Chunking documents...")
        documents = chunk_documents(documents)
        print(f"Created {len(documents)} chunks")
    
    # Create or connect to index
    create_index_if_not_exists()
    
    # Index to Pinecone
    print(f"Indexing to Pinecone (namespace: {PINECONE_NAMESPACE})...")
    try:
        vectorstore = PineconeVectorStore.from_documents(
            documents=documents,
            embedding=embeddings,
            index_name=PINECONE_INDEX,
            namespace=PINECONE_NAMESPACE,
            pinecone_api_key=PINECONE_API_KEY
        )
        print(f"Successfully indexed {len(documents)} documents to Pinecone")
    except Exception as e:
        print(f"Error indexing to Pinecone: {e}")


def clear_namespace():
    """Clear all vectors from the namespace"""
    try:
        index = pc.Index(PINECONE_INDEX)
        index.delete(delete_all=True, namespace=PINECONE_NAMESPACE)
        print(f"Cleared namespace: {PINECONE_NAMESPACE}")
    except Exception as e:
        print(f"Error clearing namespace: {e}")


def get_index_stats():
    """Get statistics about the Pinecone index"""
    try:
        index = pc.Index(PINECONE_INDEX)
        stats = index.describe_index_stats()
        print(f"\nIndex Statistics:")
        print(f"Total vectors: {stats.total_vector_count}")
        if stats.namespaces:
            for ns, info in stats.namespaces.items():
                print(f"  Namespace '{ns}': {info.vector_count} vectors")
    except Exception as e:
        print(f"Error getting stats: {e}")


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Index SAP invoices to Pinecone")
    parser.add_argument("--file", type=str, help="Path to invoice JSON file")
    parser.add_argument("--clear", action="store_true", help="Clear namespace before indexing")
    parser.add_argument("--stats", action="store_true", help="Show index statistics")
    parser.add_argument("--no-chunk", action="store_true", help="Disable document chunking")
    
    args = parser.parse_args()
    
    print("SAP Invoice Indexing Script")
    print("=" * 50)
    
    # Show stats
    if args.stats:
        get_index_stats()
    
    # Clear namespace if requested
    if args.clear:
        confirm = input(f"Are you sure you want to clear namespace '{PINECONE_NAMESPACE}'? (yes/no): ")
        if confirm.lower() == 'yes':
            clear_namespace()
    
    # Index file if provided
    if args.file:
        if not Path(args.file).exists():
            print(f"Error: File not found: {args.file}")
        else:
            index_invoices(args.file, use_chunking=not args.no_chunk)
            get_index_stats()
    
    # Interactive mode if no file provided
    if not args.file and not args.stats and not args.clear:
        print("\nUsage examples:")
        print("  python sap_invoice_indexer.py --file invoices.json")
        print("  python sap_invoice_indexer.py --file invoices.json --clear")
        print("  python sap_invoice_indexer.py --stats")
        print("  python sap_invoice_indexer.py --file invoices.json --no-chunk")
