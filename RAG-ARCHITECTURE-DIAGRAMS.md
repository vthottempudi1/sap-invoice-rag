# S/4HANA RAG System - Visual Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    S/4HANA AI Assistant with RAG                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐          ┌──────────────────────────┐
│   INDEXING WORKFLOW      │          │   CHAT WORKFLOW (RAG)    │
│   (Run Once/Scheduled)   │          │   (Real-time Queries)    │
└──────────────────────────┘          └──────────────────────────┘

INDEXING FLOW:                        CHAT FLOW:
─────────────                         ──────────

1. Trigger (Manual/Schedule)          1. User asks question
   │                                     │
   ▼                                     ▼
2. Define Business Objects            2. AI Agent receives question
   [PO: 4500000000, 4500000001]         │
   │                                     ▼
   ▼                                  3. Agent decides which tool:
3. For each business object:            ┌─────────────────────┐
   │                                    │ A. Structured data? │
   ├─→ Fetch document metadata          │ B. Document search? │
   │   (DocumentHeaderSet)               │ C. Both?            │
   │                                     └─────────────────────┘
   ├─→ Download binary content                │
   │   (OriginalContentSet/$value)            ▼
   │                                    ┌──────────┴──────────┐
   ├─→ Extract text from PDF            │                     │
   │   (PDF Parser)                     ▼                     ▼
   │                                TOOL A:              TOOL D:
   ├─→ Split into chunks            Structured           Vector Store
   │   (1000 chars, 200 overlap)    Query                Retriever
   │                                │                     │
   ├─→ Generate embeddings          │                     │
   │   (OpenAI ada-002)             ▼                     ▼
   │                              HTTP Request        Search Pinecone
   └─→ Store in vector DB         to S/4HANA          for similar docs
       (Pinecone/Qdrant)            │                     │
                                    │                     │
                                    └──────────┬──────────┘
                                               │
                                               ▼
                                        4. Combine results
                                               │
                                               ▼
                                        5. OpenAI generates
                                           answer with context
                                               │
                                               ▼
                                        6. Response to user
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        S/4HANA System                            │
│  ┌────────────────────┐  ┌──────────────────┐  ┌─────────────┐  │
│  │ Transactional Data │  │ Document Service │  │ Attachments │  │
│  │  - Sales Orders    │  │  - Metadata      │  │  - PDFs     │  │
│  │  - Purchase Orders │  │  - Binary Files  │  │  - Office   │  │
│  │  - Invoices        │  │  - Links         │  │  - Images   │  │
│  └────────────────────┘  └──────────────────┘  └─────────────┘  │
└───────────┬─────────────────────────┬─────────────────┬─────────┘
            │                         │                 │
            │ OData API               │ OData API       │ Binary
            │ JSON Response           │ JSON Metadata   │ Download
            │                         │                 │
            ▼                         ▼                 ▼
    ┌───────────────┐         ┌─────────────────────────────┐
    │  HTTP Request │         │   Document Indexer          │
    │  Tool Nodes   │         │   ┌──────────────────────┐  │
    │  (3 tools)    │         │   │ 1. Fetch metadata    │  │
    └───────┬───────┘         │   │ 2. Download content  │  │
            │                 │   │ 3. Extract text      │  │
            │                 │   │ 4. Chunk text        │  │
            │                 │   │ 5. Generate vectors  │  │
            │                 │   └──────────┬───────────┘  │
            │                 └──────────────┼──────────────┘
            │                                │
            │                                ▼
            │                         ┌────────────────┐
            │                         │ Vector Database│
            │                         │  - Pinecone    │
            │                         │  - Qdrant      │
            │                         │  - Supabase    │
            │                         └────────┬───────┘
            │                                  │
            │                                  │ Semantic
            │                                  │ Search
            └──────────┬─────────────────────┬─┘
                       │                     │
                       ▼                     ▼
              ┌─────────────────────────────────┐
              │       AI Agent (LangChain)      │
              │  ┌──────────────────────────┐   │
              │  │ System Prompt:           │   │
              │  │ "You have 4 tools..."    │   │
              │  └──────────────────────────┘   │
              └────────────┬────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  OpenAI GPT-4o-mini     │
              │  + Window Buffer Memory │
              └────────────┬────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ User Response│
                    └──────────────┘
```

## Vector Store Internals

```
INDEXING PHASE:
─────────────

SAP Document: "Purchase Order 4500000000 for Supplier ABC..."
      │
      ├─→ Text Splitter
      │   └─→ Chunk 1: "Purchase Order 4500000000 for Supplier..."
      │   └─→ Chunk 2: "...Supplier ABC, Total Amount: $10,000..."
      │   └─→ Chunk 3: "...Delivery Date: Jan 15, 2024, Terms: Net 30..."
      │
      ├─→ OpenAI Embeddings (text-embedding-ada-002)
      │   └─→ Chunk 1 Vector: [0.023, -0.145, 0.892, ..., -0.234] (1536 dims)
      │   └─→ Chunk 2 Vector: [0.112, -0.023, 0.567, ..., 0.123]
      │   └─→ Chunk 3 Vector: [-0.045, 0.234, -0.123, ..., 0.456]
      │
      └─→ Store in Pinecone/Qdrant with metadata:
          {
            "id": "po-4500000000-chunk1",
            "vector": [0.023, -0.145, ...],
            "metadata": {
              "businessObject": "4500000000",
              "documentType": "PO",
              "fileName": "PO_Confirmation.pdf",
              "chunk": 1,
              "totalChunks": 3
            }
          }

RETRIEVAL PHASE:
──────────────

User Question: "What's the delivery date for PO 4500000000?"
      │
      ├─→ OpenAI Embeddings
      │   └─→ Question Vector: [0.034, -0.156, 0.789, ..., -0.245]
      │
      ├─→ Vector Search (Cosine Similarity)
      │   └─→ Find top 5 most similar chunks
      │       Score: 0.94 → Chunk 3: "...Delivery Date: Jan 15, 2024..."
      │       Score: 0.87 → Chunk 1: "Purchase Order 4500000000..."
      │       Score: 0.72 → Chunk 2: "...Supplier ABC, Total Amount..."
      │
      └─→ Combine top chunks + question → OpenAI
          Prompt: "Given these document excerpts:
                   1. '...Delivery Date: Jan 15, 2024...'
                   2. 'Purchase Order 4500000000...'
                   Answer: What's the delivery date for PO 4500000000?"
          
          Response: "The delivery date for Purchase Order 4500000000 
                     is January 15, 2024."
```

## Tool Selection Logic

```
User Question
      │
      ▼
┌────────────────────────────────────────┐
│   AI Agent Analyzes Intent             │
│   ┌────────────────────────────────┐   │
│   │ Keywords detected:             │   │
│   │ - "sales order" → Tool A       │   │
│   │ - "purchase order" → Tool B    │   │
│   │ - "invoice" → Tool C           │   │
│   │ - "document", "PDF" → Tool D   │   │
│   │ - "what does...say" → Tool D   │   │
│   └────────────────────────────────┘   │
└────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────┐
│ Decision Tree:                   │
│                                  │
│ Is it structured data query?    │
│ ├─ Yes → Use Tools A/B/C        │
│ │         (HTTP Request)         │
│ │                                │
│ └─ No                            │
│    │                             │
│    Is it about document content? │
│    ├─ Yes → Use Tool D           │
│    │         (Vector Retriever)  │
│    │                             │
│    └─ Mixed → Use multiple tools │
└──────────────────────────────────┘
```

## Example Query Flows

### Query 1: Structured Data Only

```
User: "Show me sales orders from January 2024"
  │
  ▼
AI Agent: Recognizes "sales orders" → Use Tool A
  │
  ▼
HTTP Request: GET /SALE_SERVICE/zsales_view?$filter=...
  │
  ▼
Response: [{"OrderID": "123", "Amount": 400, ...}, ...]
  │
  ▼
AI: "Here are the sales orders from January 2024: Order 123 ($400)..."
```

### Query 2: Document Search Only

```
User: "What does the invoice PDF say about payment terms?"
  │
  ▼
AI Agent: Recognizes "PDF", "what does...say" → Use Tool D
  │
  ▼
Vector Search: Query embeddings for "payment terms invoice"
  │
  ▼
Top Results: 
  - Chunk: "Payment Terms: Net 30 days from invoice date..."
  - Chunk: "Late fees: 1.5% per month after 30 days..."
  │
  ▼
AI: "According to the invoice PDF, payment terms are Net 30 days 
     with 1.5% monthly late fees after 30 days."
```

### Query 3: Combined (Structured + Document)

```
User: "Get PO 4500000000 details and summarize attached documents"
  │
  ▼
AI Agent: Recognizes "PO" (Tool B) + "documents" (Tool D)
  │
  ├──────────────┬──────────────┐
  ▼              ▼              ▼
Tool B:      Tool D:        Tool D:
Get PO data  Search docs    Search docs
  │              │              │
  ▼              ▼              ▼
PO: {...}    Doc1: "..."    Doc2: "..."
  │              │              │
  └──────────────┴──────────────┘
                 │
                 ▼
AI: "Purchase Order 4500000000:
     - Supplier: ABC Corp
     - Amount: $10,000
     - Status: Approved
     
     Attached Documents:
     - PO Confirmation PDF: Confirms order with delivery on Jan 15
     - Supplier Quote: Original quote matching PO amount"
```

## Memory System

```
┌────────────────────────────────────────────────┐
│        Window Buffer Memory (10 messages)       │
├────────────────────────────────────────────────┤
│ [1] User: "Show me sales orders"              │
│ [2] AI: "Here are 3 sales orders..."          │
│ [3] User: "What about purchase orders?"       │
│ [4] AI: "Here are 5 purchase orders..."       │
│ [5] User: "Get details for the first one"     │
│     ┌──────────────────────────────┐           │
│     │ AI uses context: "first one" │           │
│     │ = First PO from msg [4]      │           │
│     └──────────────────────────────┘           │
│ [6] AI: "Purchase Order 4500000000..."        │
│ [7] User: "Any documents attached?"           │
│     ┌──────────────────────────────┐           │
│     │ AI knows: "attached to what?"│           │
│     │ = PO 4500000000 from msg [6] │           │
│     └──────────────────────────────┘           │
│ [8] AI: "Yes, 2 PDFs attached..."             │
│ [9] User: "Summarize the first PDF"           │
│ [10] AI: "The first PDF is..."                │
│                                                │
│ [11] User: "..." ← Oldest message dropped     │
└────────────────────────────────────────────────┘
```

## Security & Access Control

```
┌─────────────────────────────────────────────┐
│             Security Layers                  │
├─────────────────────────────────────────────┤
│                                             │
│ 1. S/4HANA Authentication                  │
│    └─→ Basic Auth: s4gui4 / Sap@123456     │
│                                             │
│ 2. n8n Credentials Store                   │
│    └─→ Encrypted credential storage         │
│                                             │
│ 3. OpenAI API Key                          │
│    └─→ Secured in n8n credentials          │
│                                             │
│ 4. Vector DB Access                        │
│    └─→ API keys for Pinecone/Qdrant        │
│                                             │
│ 5. Document Metadata Filtering             │
│    └─→ Only search docs user has access to │
│                                             │
└─────────────────────────────────────────────┘

Future Enhancement:
─────────────────
Add user authentication and document-level permissions:

User Login → n8n checks permissions → Filter vector search by:
  - User's company code
  - User's department
  - User's role (can view POs/Invoices/etc.)
```

## Performance Metrics

```
┌──────────────────────────────────────────────────┐
│            Typical Response Times                 │
├──────────────────────────────────────────────────┤
│                                                  │
│ Structured Query (Tools A/B/C):                 │
│   S/4HANA API: 200-500ms                        │
│   AI Processing: 500-1000ms                      │
│   Total: ~1-2 seconds                           │
│                                                  │
│ Document Search (Tool D):                       │
│   Question Embedding: 100ms                      │
│   Vector Search: 50-100ms                       │
│   AI Processing: 1000-2000ms                    │
│   Total: ~2-3 seconds                           │
│                                                  │
│ Combined Query (Multiple Tools):                │
│   Parallel tool execution: 500-1000ms           │
│   AI synthesis: 1500-2500ms                     │
│   Total: ~3-5 seconds                           │
│                                                  │
└──────────────────────────────────────────────────┘

Indexing Performance:
────────────────────
- 1 PDF (5 pages): ~2-3 seconds
- 100 PDFs: ~5-10 minutes
- 1000 PDFs: ~1-2 hours
```

## Scaling Considerations

```
Small Scale (<1000 documents):
└─→ In-Memory or Qdrant (Docker)
    └─→ Single n8n instance
        └─→ Works perfectly

Medium Scale (1000-10,000 documents):
└─→ Qdrant or Supabase
    └─→ Multiple n8n workers
        └─→ Load balancer for chat

Large Scale (>10,000 documents):
└─→ Pinecone or Qdrant Cloud
    └─→ n8n cluster
        └─→ Redis for memory state
            └─→ CDN for static assets
```

---

## Quick Reference: When to Use Each Component

| Component | When to Use |
|-----------|-------------|
| **Get Sales Orders** | "Show sales", "customer orders", "revenue" |
| **Get Purchase Orders** | "Show POs", "supplier orders", "procurement" |
| **Get Financial Docs** | "Show invoices", "G/L docs", "financial documents" |
| **Vector Retriever** | "What does PDF say?", "Find documents about...", "Summarize attachment" |
| **Memory** | Follow-up questions, "What was the first one?", "Tell me more" |
| **Embeddings** | Behind-the-scenes for all vector operations |

---

This architecture gives you:
✅ Structured data access (real-time queries)
✅ Unstructured data search (semantic search)
✅ Conversational context (memory)
✅ Flexible tool selection (AI agent decides)
✅ Scalable design (can grow with your needs)
