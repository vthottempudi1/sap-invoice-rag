# S/4HANA RAG (Retrieval-Augmented Generation) System Guide

## Overview
This guide explains how to build a RAG system that can search and query SAP documents (PDFs, invoices, purchase orders) using AI.

## RAG Architecture

```
User Question
    ↓
AI Agent (with RAG)
    ├── Vector Store (Pinecone/Qdrant/Supabase)
    │   └── Document Embeddings (SAP documents indexed)
    ├── Document Retriever (searches similar docs)
    ├── Context Augmentation (adds relevant docs to prompt)
    └── LLM Response (answers using document context)
```

## Components Needed

### 1. Document Indexing Workflow (Separate - Run Once/Scheduled)
**Purpose:** Fetch SAP documents and store them in vector database

**Steps:**
1. **Fetch Documents from S/4HANA**
   - Get document metadata from `CV_ATTACHMENT_SRV/DocumentHeaderSet`
   - Get binary content from `CV_ATTACHMENT_SRV/OriginalContentSet`
   
2. **Process Documents**
   - Extract text from PDFs using PDF parser
   - Split text into chunks (1000 tokens each)
   
3. **Generate Embeddings**
   - Use OpenAI Embeddings to convert text to vectors
   
4. **Store in Vector Database**
   - Pinecone (cloud, easy setup)
   - Qdrant (self-hosted)
   - Supabase (with pgvector)

### 2. RAG Chat Workflow (Your Main Workflow)
**Purpose:** Answer user questions using indexed documents

**Steps:**
1. User asks question
2. Question → Embeddings → Vector search
3. Retrieve relevant document chunks
4. Combine chunks with question
5. LLM generates answer with citations

## Implementation Options

### Option A: Full RAG with Document Indexing (Recommended)

**Required n8n Nodes:**
- Vector Store (Pinecone/Qdrant)
- OpenAI Embeddings
- Document Loader (for PDFs)
- Text Splitter
- Vector Store Retriever

**Workflow 1: Index SAP Documents (Run periodically)**
```
Schedule Trigger (daily)
    ↓
Get Documents from S/4HANA
    ↓
Loop through each document
    ↓
Download PDF content
    ↓
Extract text from PDF
    ↓
Split into chunks
    ↓
Generate embeddings
    ↓
Store in Pinecone/Qdrant
```

**Workflow 2: RAG Chat (Your main workflow)**
```
Chat Trigger
    ↓
AI Agent with Vector Store Retriever
    ├── Vector Store (Pinecone/Qdrant)
    ├── OpenAI Chat Model
    └── Memory
```

### Option B: Simple Document Search (Easier, No Indexing)

Use the existing HTTP Request tools to search document metadata without embeddings.

**Advantages:**
- No vector database needed
- Simpler setup
- Works immediately

**Disadvantages:**
- Can't search document content
- No semantic search
- Limited to metadata search

## Step-by-Step: Add RAG to Your Existing Workflow

### Prerequisites
1. **Vector Database Setup** (Choose one):
   - **Pinecone** (Easiest - Cloud):
     - Sign up at https://www.pinecone.io/
     - Create index: dimension 1536, metric cosine
     - Get API key
   
   - **Qdrant** (Self-hosted):
     - Run: `docker run -p 6333:6333 qdrant/qdrant`
     - Create collection via API
   
   - **Supabase** (PostgreSQL + pgvector):
     - Sign up at https://supabase.com/
     - Enable pgvector extension
     - Create embeddings table

### Step 1: Create Document Indexing Workflow

I'll create a separate workflow file for this.

### Step 2: Update Your Chat Workflow with RAG

The main changes to your existing workflow:
1. Add Vector Store node (Pinecone/Qdrant)
2. Add Vector Store Retriever tool
3. Update AI Agent to use retriever
4. Optionally add Document QA Chain for better document handling

## Complete RAG Workflow Files

I'll create two workflow files:
1. `n8n-s4hana-document-indexer.json` - Index documents into vector store
2. `n8n-S4HANA-OpenAI-RAG-Complete.json` - Your chat workflow with RAG

## Key Considerations

### Document Access in S/4HANA
- **Attachments service requires business object keys**
- You'll need to know: PO number, Invoice number, Material number
- Alternative: Create a scheduled job to fetch all documents daily

### Document Types Supported
- PDF (invoices, reports, contracts)
- Word/Excel (converted to text)
- Images (OCR required - use external service)

### Costs
- **Pinecone Free Tier**: 1 index, 100K vectors
- **OpenAI Embeddings**: $0.0001 per 1K tokens (~$0.10 per 1000 documents)
- **Storage**: Minimal for metadata

### Performance
- Indexing: ~1-2 seconds per document
- Search: <100ms for vector lookup
- Response: 2-5 seconds total

## Alternative: Hybrid Approach

Combine structured data tools with RAG:

```
AI Agent
├── Get Sales Orders (structured data)
├── Get Purchase Orders (structured data)
├── Get Financial Documents (structured data)
└── Search Document Knowledge Base (RAG - unstructured)
```

This gives you:
- Fast structured queries for data
- Semantic search for document content
- Best of both worlds

## Next Steps

1. **Choose vector database** (I recommend Pinecone for simplicity)
2. **Set up vector database** (create index/collection)
3. **Import document indexer workflow**
4. **Test indexing** with a few sample documents
5. **Update chat workflow** with RAG retriever
6. **Test queries** like "What does invoice #1000 say about payment terms?"

Would you like me to create the complete RAG workflow files now?
