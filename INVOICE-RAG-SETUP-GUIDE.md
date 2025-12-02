# Invoice-Only RAG System Setup Guide

## 🎯 Overview

This guide covers the **Invoice-Specific RAG System** - a specialized implementation focused exclusively on invoice document processing and analysis.

### What's Different from General RAG?

| Feature | General RAG System | Invoice-Only RAG System |
|---------|-------------------|------------------------|
| **Scope** | All S/4HANA documents (POs, Sales, Invoices) | Invoices only |
| **Tools Available** | 4 tools (Sales, Purchase, Financial, Documents) | 2 tools (Financial, Invoice Documents) |
| **Vector Storage** | Pinecone index with namespace | Pinecone `n8n-s4hana` index, `invoice-documents` namespace |
| **Use Case** | General SAP queries | Invoice analysis and processing |
| **System Prompt** | Generic SAP assistant | Invoice-specialized assistant |

---

## 📦 What You Have

### 1. **n8n-S4HANA-Invoice-RAG.json** (Chat Workflow)
- **8 nodes** focused on invoice queries
- **2 AI tools**:
  - `Get Financial Documents` - Structured invoice metadata
  - `Invoice Document Knowledge Base` - Vector search through invoice PDFs
- **Pinecone storage**: Index `n8n-s4hana`, Namespace `invoice-documents`
- **Optimized system prompt** for invoice-specific queries

### 2. **n8n-invoice-document-indexer.json** (Indexer Workflow)
- **12 nodes** to index invoice PDFs
- Fetches documents attached to invoice numbers
- Processes only invoice-related PDFs
- Stores in Pinecone index `n8n-s4hana` with namespace `invoice-documents`
- **Metadata stored**: invoiceNumber, documentType, fileName, fileType, indexedDate

### 3. **Pinecone Configuration**
- **Index**: `n8n-s4hana`
- **Namespace**: `invoice-documents` (separates invoice data from other documents)
- **Dimensions**: 1536 (OpenAI embeddings)
- **Metric**: Cosine similarity
- **Account**: vthottempudi1@gmail.com

---

## 🚀 Quick Start (5 Steps)

### Step 1: Configure Pinecone Credentials in n8n

1. Go to n8n Cloud: https://vthottempudi1.app.n8n.cloud
2. Go to **Settings** → **Credentials**
3. Click **"Add Credential"** → Search for **"Pinecone"**
4. Enter your Pinecone API key
5. **Name**: "Pinecone Invoice API"
6. **Save**
7. Copy the credential ID for later use

**Pinecone Setup**:
- **Account**: vthottempudi1@gmail.com
- **Index**: `n8n-s4hana`
- **Namespace**: `invoice-documents`
- **Dimensions**: 1536 (OpenAI text-embedding-ada-002)
- **Metric**: Cosine

**If index doesn't exist yet**, create it in Pinecone dashboard:
1. Go to https://app.pinecone.io
2. Create index: `n8n-s4hana`
3. Dimensions: 1536
4. Metric: Cosine
5. Namespace will be auto-created when first document is indexed

---

### Step 2: Import Chat Workflow to n8n

1. Open your n8n Cloud: https://vthottempudi1.app.n8n.cloud
2. Click **"Add workflow"** → **"Import from file"**
3. Select `n8n-S4HANA-Invoice-RAG.json`
4. Click **"Import"**
5. **Activate** the workflow (toggle in top-right)

**What you get**:
- Chat interface for invoice queries
- 2 AI tools ready to use
- Financial Documents tool works immediately
- Invoice Document Knowledge Base needs indexing (Step 4)

---

### Step 3: Test Structured Invoice Queries (Works Immediately)

Click **"Chat"** button in workflow and try:

```
"Show me all invoices"
"List financial documents"
"What invoices were posted this year?"
"Show invoice amounts and dates"
```

**How it works**:
- AI uses `Get Financial Documents` tool
- Queries SAP OData service: `FAC_FINANCIAL_DOCUMENT_SRV_01/Headers`
- Returns structured data (invoice numbers, amounts, dates, company codes)
- **No indexing required** - works immediately

---

### Step 4: Import and Run Invoice Indexer

#### 4.1 Get Real Invoice Numbers

In the chat, ask:
```
"Show me all invoices"
```

Copy invoice numbers from the response (e.g., "1000", "4900000000", "4900000001").

#### 4.2 Import Indexer Workflow

1. Go to n8n Cloud
2. Click **"Add workflow"** → **"Import from file"**
3. Select `n8n-invoice-document-indexer.json`
4. Click **"Import"**

#### 4.3 Configure Invoice Numbers

1. Open the indexer workflow
2. Find **"Set Invoice Numbers"** node (2nd node)
3. Update with your real invoice numbers:

```json
{
  "invoices": ["1000", "4900000000", "4900000001", "4900000002"]
}
```

**Important**: Use invoice numbers that actually have PDF attachments in your S/4HANA system.

#### 4.4 Execute Indexer

1. Click **"Execute Workflow"** button (play icon)
2. Watch the execution flow:

```
Manual Trigger
  ↓
Set Invoice Numbers (defines 4 invoices)
  ↓
Split Invoices (creates 4 parallel branches)
  ↓
For Each Invoice:
  ↓
  Loop Invoices (sets currentInvoice variable)
    ↓
  Get Invoice Document Metadata
    ↓
  Flatten Document List
    ↓
  Filter PDFs Only
    ↓
  Download Invoice PDF Content
    ↓
  Extract Invoice PDF Text
    ↓
  Split Text into Chunks (1000 chars, 200 overlap)
    ↓
  Store in Qdrant (with OpenAI embeddings)
```

**Expected Results**:
- ✅ All nodes show green checkmarks
- ✅ Multiple chunks created per invoice (depending on PDF size)
- ✅ Vectors stored in Qdrant

**Execution Time**: ~2-3 seconds per invoice PDF

---

### Step 5: Verify Indexing & Test RAG

#### 5.1 Check Vectors in Pinecone

**Option 1: Via Pinecone Dashboard**
1. Go to https://app.pinecone.io
2. Select index `n8n-s4hana`
3. Check namespace `invoice-documents`
4. View vector count

**Option 2: Via Pinecone API** (if you have API key)
```powershell
$headers = @{
    "Api-Key" = "YOUR_PINECONE_API_KEY"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "https://YOUR-INDEX.pinecone.io/describe_index_stats" `
  -Method POST -Headers $headers -Body '{"namespace": "invoice-documents"}'
```

**Expected Output**:
```json
{
  "namespaces": {
    "invoice-documents": {
      "vectorCount": 15
    }
  }
}
```

If you indexed 4 invoices with ~3-4 chunks each = ~12-16 vectors.

**If vectorCount = 0**:
- Invoice numbers don't have PDF attachments
- Try different invoice numbers
- Check troubleshooting section below

#### 5.2 Test Invoice Document Search

Go back to the chat workflow and ask:

```
"What does invoice 1000 say about payment terms?"
"Find invoices mentioning shipping costs"
"Show me the line items in invoice 4900000000"
"What are the terms and conditions in my invoices?"
"Summarize the content of invoice PDFs"
```

**How it works**:
- AI uses `Invoice Document Knowledge Base` tool
- Converts question to embedding (1536-dim vector)
- Searches Qdrant `invoice-documents` collection
- Retrieves top 5 most relevant chunks
- Generates answer based on actual PDF content

**Response should include**:
- ✅ Specific content from invoice PDFs
- ✅ Citation: "From Invoice Document Knowledge Base"
- ✅ Invoice numbers and file names referenced
- ✅ Relevant text snippets from PDFs

---

## 🔍 Understanding the Invoice RAG Flow

### Query Flow Diagram

```
User Question: "What are the payment terms in invoice 1000?"
    ↓
AI Agent analyzes question
    ↓
Decision: This is about invoice content → Use Invoice Document Knowledge Base
    ↓
Vector Store Retriever
    ↓
Question → OpenAI Embeddings → Vector [1536 numbers]
    ↓
Pinecone searches index n8n-s4hana, namespace invoice-documents
    ↓
Finds top 5 similar chunks (cosine similarity)
    ↓
Returns chunks:
  - Chunk 1: "Invoice 1000 Payment Terms: Net 30 days..."
  - Chunk 2: "Due Date: January 15, 2024..."
  - Chunk 3: "Late payment penalty: 2% per month..."
    ↓
AI Agent receives chunks + original question
    ↓
OpenAI Chat Model generates answer
    ↓
Response: "Invoice 1000 has payment terms of Net 30 days, 
           due on January 15, 2024, with a late payment 
           penalty of 2% per month. (Source: Invoice Document 
           Knowledge Base, file: Invoice_1000.pdf)"
```

### Indexing Flow Diagram

```
Invoice Numbers: ["1000", "4900000000"]
    ↓
For each invoice:
    ↓
Get Document Metadata (CV_ATTACHMENT_SRV)
  Response: [{FileName: "Invoice_1000.pdf", MimeType: "application/pdf"}]
    ↓
Filter: Keep only PDFs
    ↓
Download PDF Binary (CV_ATTACHMENT_SRV/OriginalContentSet/$value)
    ↓
Extract Text from PDF
  Result: "INVOICE #1000\nDate: 2024-01-01\nCustomer: ABC Corp\n
           Total: $5,000\nPayment Terms: Net 30..."
    ↓
Split into Chunks (1000 chars, 200 overlap)
  - Chunk 1: "INVOICE #1000 Date: 2024-01-01 Customer: ABC Corp..."
  - Chunk 2: "...ABC Corp Total: $5,000 Payment Terms: Net 30..."
  - Chunk 3: "...Net 30 days Due Date: Jan 15, 2024..."
    ↓
For each chunk:
    ↓
Generate Embedding (OpenAI text-embedding-ada-002)
  Input: "INVOICE #1000 Date: 2024-01-01..."
  Output: [0.023, -0.145, 0.892, ..., -0.234] (1536 numbers)
    ↓
Store in Pinecone with metadata:
  - Index: n8n-s4hana
  - Namespace: invoice-documents
  - Vector ID: auto-generated
  - Metadata:
    * invoiceNumber: "1000"
    * documentType: "INV"
    * fileName: "Invoice_1000.pdf"
    * fileType: "application/pdf"
    * sourceSystem: "S4HANA"
    * indexedDate: "2024-11-22T10:30:00Z"
```

---

## 🎯 Example Use Cases

### Use Case 1: Payment Terms Analysis

**Question**: "What are the payment terms across all indexed invoices?"

**Flow**:
1. AI uses `Invoice Document Knowledge Base`
2. Searches for chunks mentioning "payment terms"
3. Returns: "Net 30", "Due on receipt", "2/10 Net 30", etc.
4. AI summarizes all payment terms found

### Use Case 2: Invoice Amount Verification

**Question**: "Show me invoices over $10,000 and their terms"

**Flow**:
1. AI uses **both tools**:
   - `Get Financial Documents` → Filters invoices by amount > $10,000
   - `Invoice Document Knowledge Base` → Gets payment terms from PDFs
2. Combines structured data + document content
3. Returns: "Invoice 4900000000: $15,000, payment terms: Net 60 days"

### Use Case 3: Line Item Extraction

**Question**: "What line items are in invoice 1000?"

**Flow**:
1. AI uses `Invoice Document Knowledge Base`
2. Searches for chunks from invoice 1000 containing "line items" or "description"
3. Returns extracted text from PDF showing items, quantities, prices

### Use Case 4: Dispute Resolution

**Question**: "Find all invoices mentioning 'late delivery' or 'damaged goods'"

**Flow**:
1. AI uses `Invoice Document Knowledge Base`
2. Semantic search finds relevant chunks (even if exact words differ)
3. Returns invoices with notes/comments about delivery issues

---

## 🛠️ Troubleshooting

### Problem 1: Indexer Returns "No documents found"

**Cause**: Invoice numbers don't have PDF attachments in S/4HANA.

**Solution**:
1. Test attachment service manually:
   ```powershell
   curl.exe -k -u s4gui4:Sap@123456 `
     "https://49.206.196.74:8009/sap/opu/odata/sap/CV_ATTACHMENT_SRV/DocumentHeaderSet?`$format=json&`$filter=ObjectKey eq '1000'"
   ```
2. Check response - should have `d.results` array with attachments
3. If empty, try different invoice numbers
4. Ask in chat: "Which invoices have the most documents attached?"

### Problem 2: Vectors Not Increasing in Pinecone

**Diagnosis**:
1. Check Pinecone dashboard: https://app.pinecone.io
2. Select index `n8n-s4hana`
3. View namespace `invoice-documents`
4. Check vector count

**Possible Causes**:
- ❌ Indexer failed (check execution logs in n8n)
- ❌ PDFs are scanned images (text extraction fails - need OCR)
- ❌ Wrong namespace (should be `invoice-documents`)
- ❌ Pinecone credential not configured in n8n
- ❌ Pinecone index doesn't exist

**Solutions**:
```powershell
# Verify Pinecone credential in n8n
# Go to Settings → Credentials → Find "Pinecone Invoice API"
# Make sure API key is valid

# Check if index exists in Pinecone dashboard
# Create if missing:
# - Name: n8n-s4hana
# - Dimensions: 1536
# - Metric: Cosine
```

### Problem 3: AI Not Using Invoice Document Knowledge Base

**Symptoms**:
- Ask: "What does invoice 1000 say?"
- AI responds: "I don't have access to invoice content"

**Diagnosis**:
1. Check vectors indexed in Pinecone dashboard:
   - Go to https://app.pinecone.io
   - Index `n8n-s4hana` → Namespace `invoice-documents`
   - Should show vectors > 0

2. Check workflow connections:
   - OpenAI Embeddings → Pinecone Vector Store (ai_embedding)
   - Pinecone Vector Store → Vector Store Retriever (ai_vectorStore)
   - Vector Store Retriever → AI Agent (ai_tool)

3. Verify Pinecone credential is configured in both workflows

**Solutions**:
- Make question explicit: "Search the invoice PDFs for payment terms"
- Verify indexer ran successfully
- Check system prompt includes Invoice Document Knowledge Base
- Ensure Pinecone credential is properly linked in nodes

### Problem 4: High OpenAI Costs

**Cost Breakdown**:
- Indexing: ~$0.0001 per 1000 tokens (text-embedding-ada-002)
- Chat queries: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens (gpt-4o-mini)

**Example Costs**:
- 100 invoice PDFs, avg 5 chunks each = 500 embeddings ≈ $0.05
- 1000 chat queries ≈ $2-5

**Optimization**:
1. Increase chunk size to reduce chunks:
   ```json
   "chunkSize": 1500,
   "chunkOverlap": 200
   ```
2. Index only active/recent invoices
3. Use lower topK (retrieve 3 instead of 5):
   ```json
   "topK": 3
   ```

---

## 📊 Monitoring & Maintenance

### Daily Checks

```powershell
# Check Qdrant status
docker ps | Select-String qdrant

# Check collection health
Invoke-RestMethod -Uri "http://localhost:6333/collections/invoice-documents" | 
  Select-Object -ExpandProperty result | 
  Format-Table status, vectors_count, points_count -AutoSize
```

### Weekly Maintenance

```powershell
# Check disk usage
Invoke-RestMethod -Uri "http://localhost:6333/collections/invoice-documents" | 
  Select-Object -ExpandProperty result | 
  Select-Object disk_data_size

# Backup Qdrant data
docker exec qdrant tar -czf /qdrant/storage/backup.tar.gz /qdrant/storage/collections/invoice-documents
docker cp qdrant:/qdrant/storage/backup.tar.gz ./backups/
```

### Monthly: Re-index New Invoices

1. Get new invoice numbers:
   ```
   Ask chat: "Show me invoices from last month"
   ```
2. Update indexer with new numbers
3. Run indexer workflow
4. Verify vectors increased

---

## 🔄 Updating Invoice Numbers

### Option 1: Manual Update (Recommended for Ad-Hoc)

Edit **"Set Invoice Numbers"** node:
```json
{
  "invoices": ["1000", "4900000000", "NEW_INVOICE_1", "NEW_INVOICE_2"]
}
```

### Option 2: Dynamic from Chat (Advanced)

Modify indexer to accept input from chat:
1. Replace "Manual Trigger" with "Webhook Trigger"
2. Accept invoice numbers as parameter
3. Chat workflow can trigger indexer with specific invoices

---

## 🎓 Advanced: Scheduled Re-Indexing

### Convert to Scheduled Workflow

1. Open `n8n-invoice-document-indexer.json`
2. Replace **"Manual Trigger"** with **"Schedule Trigger"**:
   - Trigger: Daily at 2:00 AM
   - OR: Weekly on Mondays at 1:00 AM
3. Configure dynamic invoice fetching:

```json
// Add "Get Recent Invoices" HTTP node before "Set Invoice Numbers"
{
  "url": "https://49.206.196.74:8009/sap/opu/odata/sap/FAC_FINANCIAL_DOCUMENT_SRV_01/Headers?$format=json&$filter=PostingDate ge datetime'2024-11-01T00:00:00'",
  "authentication": "httpBasicAuth",
  // Extract invoice numbers from response
  // Pass to "Set Invoice Numbers"
}
```

4. **Activate** workflow
5. Invoices automatically indexed daily

---

## 📈 Success Criteria

### ✅ System is Working When:

- [ ] Qdrant collection `invoice-documents` shows `status: green`
- [ ] `vectors_count > 0` (documents indexed)
- [ ] Chat responds to: "Show me invoices" (Financial Documents tool)
- [ ] Chat responds to: "What does invoice X say?" (Invoice Document Knowledge Base)
- [ ] AI cites sources correctly
- [ ] Follow-up questions work (memory active)
- [ ] Response time < 5 seconds
- [ ] Relevant invoice content returned

### 🎯 Quality Checks

**Test Query Set**:
1. "Show me all invoices" → Should list invoices
2. "What are the payment terms in invoice 1000?" → Should extract from PDF
3. "Find invoices over $5000" → Should use Financial Documents
4. "Which invoices mention shipping?" → Should use Invoice Knowledge Base
5. "Show invoice 1000 and its terms" → Should use BOTH tools

---

## 💡 Tips & Best Practices

### 1. Question Phrasing

**Good Questions** (clear intent):
- "What does the invoice PDF say about delivery?"
- "Search invoice documents for late fees"
- "Extract line items from invoice 1000"

**Vague Questions** (AI might guess wrong):
- "Tell me about invoice 1000" (metadata or content?)
- "Find invoice stuff" (too vague)

### 2. Metadata Usage

Each vector stored in Pinecone includes:
- `invoiceNumber` - Filter by specific invoice
- `fileName` - Trace back to source file
- `indexedDate` - Know when it was indexed
- `documentType` - Category of document

**Future Enhancement**: Add metadata filtering in Vector Retriever:
```json
"filter": {
  "invoiceNumber": {"$eq": "1000"}
}
```

This allows queries like:
- "Search only invoice 1000 documents"
- "Find in invoices indexed this week"
- "Search PDFs only (not scanned docs)"

### 3. Performance Optimization

- **For < 100 invoices**: Current setup works great
- **For 100-1000 invoices**: Consider namespace organization by year/type
- **For > 1000 invoices**: Use metadata filtering, increase topK, upgrade Pinecone plan

---

## 🆚 When to Use Invoice RAG vs General RAG

### Use **Invoice RAG** When:
- ✅ Questions specifically about invoices
- ✅ Need to analyze invoice content/terms
- ✅ Processing invoice approvals/disputes
- ✅ Extracting invoice line items
- ✅ Compliance/audit queries on invoices

### Use **General RAG** When:
- ✅ Need sales order + invoice information
- ✅ Cross-functional queries (POs + invoices)
- ✅ General SAP document search
- ✅ Don't know document type in advance

### Use **Both** When:
- ✅ Complex procurement-to-pay queries
- ✅ "Show me PO 4500000000 and related invoices with their terms"
- ✅ Need multiple document types

---

## 📝 Summary

You now have a **specialized Invoice RAG system** that:

✅ Focuses exclusively on invoice documents
✅ Uses Pinecone cloud vector database (index: `n8n-s4hana`, namespace: `invoice-documents`)
✅ Provides 2 optimized tools (Financial + Invoice Knowledge Base)
✅ Stores invoice-specific metadata
✅ Enables semantic search through invoice PDFs
✅ Works alongside general RAG system (different namespaces)

**Next Steps**:
1. Configure Pinecone credential in n8n Cloud
2. Import both workflows to n8n Cloud
3. Test Financial Documents tool (works immediately)
4. Run invoice indexer with real invoice numbers
5. Test Invoice Document Knowledge Base
6. Combine with general RAG for comprehensive SAP AI assistant

**Files Created**:
- `n8n-S4HANA-Invoice-RAG.json` - Chat workflow
- `n8n-invoice-document-indexer.json` - Indexer workflow
- `INVOICE-RAG-SETUP-GUIDE.md` - This guide

**Pinecone Configuration**:
- **Account**: vthottempudi1@gmail.com
- **Index**: n8n-s4hana
- **Namespace**: invoice-documents (separates from general documents)
- **Dimensions**: 1536 (OpenAI embeddings)
- **Metric**: Cosine similarity

---

## 🔗 Resources

- **General RAG Guide**: `HOW-TO-USE-RAG-SYSTEM.md`
- **Architecture**: `RAG-ARCHITECTURE-DIAGRAMS.md`
- **Quick Reference**: `RAG-QUICK-REFERENCE.md`
- **Pinecone Docs**: https://docs.pinecone.io/
- **Pinecone Dashboard**: https://app.pinecone.io/

---

**Questions?** Ask the AI assistant in either chat workflow! 🤖
