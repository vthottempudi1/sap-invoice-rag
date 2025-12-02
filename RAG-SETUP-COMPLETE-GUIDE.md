# S/4HANA RAG System - Complete Setup Guide

## What You'll Build

A complete AI system that can:
1. **Query structured data** (sales orders, purchase orders, invoices)
2. **Search documents** (PDFs, attachments) using semantic search
3. **Answer questions** about document content using RAG (Retrieval-Augmented Generation)

## Files Created

1. **n8n-S4HANA-OpenAI-RAG-Complete.json** - Main chat workflow with RAG
2. **n8n-s4hana-document-indexer.json** - Document indexing workflow
3. **S4HANA-RAG-SYSTEM-GUIDE.md** - Architecture guide

## Prerequisites

### 1. Pinecone Account (Vector Database)
**Why:** Store document embeddings for semantic search

**Steps:**
1. Go to https://www.pinecone.io/
2. Sign up for free account
3. Create a new index:
   - **Name:** `s4hana-documents`
   - **Dimensions:** `1536` (OpenAI embedding size)
   - **Metric:** `cosine`
   - **Pod type:** `s1.x1` (free tier)
4. Get your API key from Settings → API Keys
5. Note your **Environment** (e.g., `us-east-1-aws`)

### 2. n8n Credentials Setup

Add these credentials in n8n:

#### Pinecone API Credential
1. In n8n: Settings → Credentials → Add Credential
2. Search for "Pinecone"
3. Enter:
   - **API Key:** (from Pinecone dashboard)
   - **Environment:** (e.g., us-east-1-aws)
4. Save as "Pinecone API"

#### OpenAI API Credential
(You already have this, but verify it has permissions for embeddings)
1. Your existing OpenAI credential works
2. Ensure it has access to `text-embedding-ada-002` model

#### SAP S/4HANA Basic Auth
(You already have this)
- Username: s4gui4
- Password: Sap@123456

## Step-by-Step Setup

### Step 1: Import the Document Indexer Workflow

1. Open n8n
2. Click "Import from file"
3. Select `n8n-s4hana-document-indexer.json`
4. Update credential IDs:
   - Replace `"id": "sap-basic-auth-id"` with your actual SAP credential ID
   - Replace `"id": "pinecone-credential-id"` with your Pinecone credential ID
   - Replace `"id": "openai-credential-id"` with your OpenAI credential ID
5. Save the workflow

### Step 2: Configure Business Objects to Index

In the "Set Business Objects" node, update these arrays with actual IDs from your system:

```javascript
{
  "purchaseOrders": ["4500000000", "4500000001", "4500000002"],
  "invoices": ["1000", "4900000000"]
}
```

**How to find these:**
- Run your existing workflow to query purchase orders
- Get the PO numbers from the results
- Update this array with real PO numbers that have attachments

### Step 3: Test Document Indexing

1. Click "Execute Workflow" (manual trigger)
2. Watch the execution flow:
   - Splits purchase orders
   - Fetches document metadata for each PO
   - Downloads PDF content
   - Extracts text from PDFs
   - Splits into chunks
   - Generates embeddings
   - Stores in Pinecone
3. Check for errors in each node
4. Verify in Pinecone dashboard that vectors were created

**Expected Results:**
- If 3 POs each have 2 PDFs, you'll get ~6 documents indexed
- Each document split into chunks (if large)
- Total vectors in Pinecone = number of chunks created

### Step 4: Import the RAG Chat Workflow

1. Import `n8n-S4HANA-OpenAI-RAG-Complete.json`
2. Update credential IDs (same as step 1)
3. **Important:** Update the Pinecone index name in "Pinecone Vector Store" node to `s4hana-documents`
4. Save and activate the workflow

### Step 5: Test RAG System

Open the chat interface and try these queries:

**Test 1 - Structured Data (existing functionality):**
```
User: Show me sales orders
AI: [Uses Get Sales Orders tool - should work as before]
```

**Test 2 - Document Search (new RAG functionality):**
```
User: What documents are attached to purchase order 4500000000?
AI: [Uses Document Knowledge Base tool - searches vector store]
```

**Test 3 - Document Content:**
```
User: What does the PDF for invoice 1000 say about payment terms?
AI: [Retrieves relevant document chunks and answers based on content]
```

**Test 4 - Combined Query:**
```
User: Show me the purchase order for PO 4500000000 and summarize any attached documents
AI: [Uses both Get Purchase Orders + Document Knowledge Base]
```

## Workflow Architecture

### Main Chat Workflow (n8n-S4HANA-OpenAI-RAG-Complete.json)

```
Chat Trigger
    ↓
AI Agent (with system prompt explaining all 4 tools)
    ├─→ Get Sales Orders (HTTP Request to ZSALE_SERVICE)
    ├─→ Get Purchase Orders (HTTP Request to C_PURCHASEORDER_FS_SRV)
    ├─→ Get Financial Documents (HTTP Request to FAC_FINANCIAL_DOCUMENT_SRV_01)
    └─→ Vector Store Retriever (searches Pinecone for document content)
         ├─→ Pinecone Vector Store (mode: load)
         └─→ OpenAI Embeddings (text-embedding-ada-002)
    ├─→ OpenAI Chat Model (gpt-4o-mini, temp 0.3)
    └─→ Window Buffer Memory (10 messages)
```

### Document Indexer Workflow (n8n-s4hana-document-indexer.json)

```
Manual Trigger
    ↓
Set Business Objects (define PO/Invoice numbers to index)
    ↓
Split Purchase Orders (loop through each)
    ↓
Get Document Metadata (CV_ATTACHMENT_SRV/DocumentHeaderSet)
    ↓
Flatten Document List (prepare for processing)
    ↓
Filter PDFs Only (skip non-PDF files)
    ↓
Download Document Content (CV_ATTACHMENT_SRV/OriginalContentSet)
    ↓
Extract PDF Text (n8n PDF node)
    ↓
Split Text into Chunks (1000 chars, 200 overlap)
    ↓
Store in Pinecone (with metadata: businessObject, documentType, fileName)
    └─→ OpenAI Embeddings (text-embedding-ada-002)
```

## Understanding the RAG Flow

When a user asks a question about documents:

1. **Question Received:** "What's in the invoice PDF?"
2. **AI Agent Decides:** This is a document content query → use Vector Store Retriever
3. **Embedding Generated:** Question converted to embedding vector
4. **Vector Search:** Pinecone finds top 5 similar document chunks
5. **Context Assembled:** Retrieved chunks added to AI prompt
6. **Answer Generated:** OpenAI responds using document context
7. **Citation:** AI cites the source (document name, PO number)

## Metadata Stored with Each Document

When documents are indexed, metadata is attached:

```json
{
  "businessObject": "4500000000",
  "documentType": "PUR",
  "documentNumber": "000001",
  "fileName": "PO_Confirmation.pdf",
  "fileType": "application/pdf",
  "sourceSystem": "S4HANA"
}
```

This allows filtering: "Find documents for PO 4500000000" or "Show me all PDF invoices"

## Cost Estimation

### One-Time Indexing Costs (per 100 documents):
- **OpenAI Embeddings:** ~$0.01 (100 docs × 1000 tokens avg × $0.0001/1K tokens)
- **Pinecone Storage:** Free tier (up to 100K vectors)
- **Total:** ~$0.01 per 100 documents

### Per-Query Costs:
- **Embedding Query:** ~$0.0001
- **OpenAI Chat:** ~$0.001-0.01 (depends on response length)
- **Total:** ~$0.001 per query

**Monthly Estimate (100 queries/day):**
- 3,000 queries × $0.001 = **$3/month**
- Plus initial indexing: **$0.10** (for 1000 documents)

## Troubleshooting

### Issue: "Pinecone index not found"
**Solution:**
1. Verify index name is exactly `s4hana-documents`
2. Check Pinecone dashboard that index was created
3. Verify API key and environment are correct

### Issue: "No documents found in vector search"
**Solution:**
1. Run the indexer workflow first
2. Check Pinecone dashboard → Indexes → s4hana-documents → Statistics
3. Verify vector count > 0
4. Check indexer workflow execution for errors

### Issue: "Document download failed"
**Solution:**
1. Verify the PO/Invoice numbers in "Set Business Objects" are valid
2. Check that documents are actually attached to those objects in S/4HANA
3. Test document API manually:
   ```bash
   curl -k -u s4gui4:Sap@123456 \
     "https://49.206.196.74:8009/sap/opu/odata/sap/CV_ATTACHMENT_SRV/DocumentHeaderSet?\$filter=ObjectKey eq '4500000000'"
   ```

### Issue: "PDF extraction failed"
**Solution:**
1. Check if PDF is text-based (not scanned image)
2. For scanned PDFs, you'd need OCR (not included in basic n8n PDF node)
3. Try a different PDF or convert scanned PDFs to text first

### Issue: "AI not using Document Knowledge Base tool"
**Solution:**
1. Make your question explicitly about documents: "What's in the PDF?" instead of "Show me data"
2. Check AI Agent system prompt includes Document Knowledge Base description
3. Verify Vector Store Retriever is connected to AI Agent

### Issue: "Embeddings cost too high"
**Solution:**
1. Reduce chunk size from 1000 to 500 chars
2. Index only critical documents first
3. Use text summarization before embedding (condense large docs)

## Advanced Configurations

### Add More Document Sources

To index invoices in addition to POs:

1. Duplicate the "Split Purchase Orders" branch
2. Create "Split Invoices" → "Loop Invoices" → "Get Invoice Documents"
3. Update filter: `ObjectKey eq '{{ $json.currentInvoice }}'`
4. Merge both branches before "Filter PDFs Only"

### Filter by Document Type in Queries

Modify Vector Store Retriever to add filter:

```json
{
  "filter": {
    "documentType": "INV"  // Only search invoices
  }
}
```

### Schedule Automatic Indexing

Replace "Manual Trigger" with "Schedule Trigger":
- **Interval:** Daily at 2 AM
- **Timezone:** Your timezone
- This keeps document index fresh automatically

### Add Support for Office Documents

After "Filter PDFs Only":
1. Add "Filter Office Docs" (application/vnd.openxmlformats)
2. Add "Extract Office Text" node (uses different extraction)
3. Merge with PDF branch before "Split Text"

### Increase Retrieval Accuracy

In "Vector Store Retriever" node:
- Increase `topK` from 5 to 10 (retrieve more chunks)
- Add metadata filtering for specific document types
- Adjust chunk overlap from 200 to 300 (more context)

## Next Steps

After successful setup:

1. **Index more documents:**
   - Add more PO/Invoice numbers to indexer
   - Run indexer workflow weekly
   
2. **Monitor performance:**
   - Check Pinecone dashboard for vector count
   - Review OpenAI usage for cost tracking
   
3. **Enhance queries:**
   - Train users to ask document-specific questions
   - Create example prompts for common use cases
   
4. **Scale up:**
   - Move to scheduled indexing
   - Add more document types (material specs, contracts)
   - Implement document expiry (delete old embeddings)

## Support Resources

- **n8n Documentation:** https://docs.n8n.io/
- **Pinecone Docs:** https://docs.pinecone.io/
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings
- **SAP OData Services:** Your S/4HANA system documentation

## Example Queries to Try

Once everything is set up:

```
"Show me sales orders for customer X"  
→ Uses Get Sales Orders tool

"What documents are attached to PO 4500000000?"  
→ Uses Document Knowledge Base (RAG)

"Summarize the PDF for invoice 1000"  
→ Uses Document Knowledge Base (RAG)

"Find purchase orders over $10,000 and check if they have approval documents"  
→ Uses Get Purchase Orders + Document Knowledge Base

"What does the contract say about payment terms?"  
→ Uses Document Knowledge Base (RAG)

"Show me all financial documents from January 2024"  
→ Uses Get Financial Documents tool

"Compare the invoice amount in the system vs what's in the PDF"  
→ Uses Get Financial Documents + Document Knowledge Base
```

---

## Quick Start Checklist

- [ ] Create Pinecone account and index (s4hana-documents, 1536 dimensions)
- [ ] Add Pinecone credential in n8n
- [ ] Import `n8n-s4hana-document-indexer.json`
- [ ] Update credential IDs in indexer workflow
- [ ] Update business object IDs (real PO/Invoice numbers)
- [ ] Run indexer workflow and verify vectors in Pinecone
- [ ] Import `n8n-S4HANA-OpenAI-RAG-Complete.json`
- [ ] Update credential IDs in chat workflow
- [ ] Activate chat workflow
- [ ] Test with sample queries
- [ ] Success! You now have RAG-powered S/4HANA AI assistant

---

**Estimated Setup Time:** 30-45 minutes  
**Difficulty:** Intermediate  
**Cost:** ~$3-5/month (Pinecone free tier + OpenAI usage)
