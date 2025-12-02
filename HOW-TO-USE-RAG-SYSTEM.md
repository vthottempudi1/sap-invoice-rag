# How to Use the RAG System - Step by Step Guide

## ✅ What's Already Done

1. ✅ Qdrant vector database is running (localhost:6333)
2. ✅ Collection `s4hana-documents` created (1536 dimensions)
3. ✅ Chat workflow updated with your credentials
4. ✅ Document indexer workflow updated with your credentials
5. ✅ All nodes configured to use Qdrant

## 📋 Step-by-Step Instructions

### Step 1: Import the Chat Workflow

1. Open your n8n instance: https://vthottempudi1.app.n8n.cloud
2. Click **"Add workflow"** → **"Import from file"**
3. Select: `n8n-S4HANA-OpenAI-RAG-Complete.json`
4. Click **"Import"**
5. The workflow will open with all nodes connected

**What you'll see:**
- 10 nodes total
- Chat Trigger → AI Agent → 4 Tools
- Qdrant Vector Store with embeddings

### Step 2: Import the Document Indexer Workflow

1. Click **"Add workflow"** → **"Import from file"**
2. Select: `n8n-s4hana-document-indexer.json`
3. Click **"Import"**
4. This is your document indexing workflow

**What you'll see:**
- Manual Trigger node (to start indexing)
- Nodes to fetch, process, and embed documents

### Step 3: Test the Chat Workflow (Without RAG First)

1. Open the **S4HANA AI Agent with RAG** workflow
2. Click **"Activate"** toggle (top right)
3. Click the **"Chat"** button to open chat interface
4. Test structured queries:

```
You: Show me sales orders
AI: [Will use Get Sales Orders tool and show results]

You: Get purchase orders
AI: [Will use Get Purchase Orders tool and show results]

You: Show me financial documents
AI: [Will use Get Financial Documents tool and show results]
```

✅ **Success!** The 3 data tools are working.

⚠️ **Note:** Document search won't work yet because Qdrant is empty.

### Step 4: Run the Document Indexer (Populate Qdrant)

Now we need to add documents to Qdrant so RAG can search them.

1. Open the **S4HANA Document Indexer (RAG)** workflow
2. Find the **"Set Business Objects"** node
3. Update the PO numbers with real ones from your system:

```json
{
  "purchaseOrders": ["4500000000", "4500000001", "4500000002"],
  "invoices": ["1000", "4900000000"]
}
```

**How to find real PO numbers:**
- Go back to your chat workflow
- Ask: "Show me purchase orders"
- Copy the PO numbers from the response
- Paste them into the indexer's "Set Business Objects" node

4. Click **"Execute Workflow"** (the play button)
5. Watch the execution:
   - ✅ Splits purchase orders
   - ✅ Fetches document metadata for each PO
   - ✅ Downloads PDF content
   - ✅ Extracts text from PDFs
   - ✅ Splits text into chunks
   - ✅ Generates embeddings
   - ✅ Stores in Qdrant

### Step 5: Verify Documents Were Indexed

Check Qdrant to see if documents were added:

```powershell
Invoke-RestMethod -Uri "http://localhost:6333/collections/s4hana-documents" | 
  Select-Object -ExpandProperty result | 
  Select-Object -ExpandProperty vectors_count
```

**Expected output:** A number > 0 (e.g., 15 if you indexed 3 POs with 5 chunks each)

If you see `0`, it means:
- The PO numbers don't have attachments, OR
- The document service requires different parameters, OR
- The documents aren't PDFs

### Step 6: Test RAG Document Search

Go back to your **chat workflow** and try document queries:

```
You: What documents are attached to purchase order 4500000000?
AI: [Will use Document Knowledge Base tool and search Qdrant]

You: What does the PDF say about delivery terms?
AI: [Searches embedded document content and answers]

You: Find documents mentioning payment schedule
AI: [Semantic search through all indexed documents]

You: Show me PO 4500000000 and summarize its attachments
AI: [Uses Get Purchase Orders + Document Knowledge Base]
```

## 🎯 Understanding the Flow

### When You Ask About Structured Data:
```
"Show me sales orders" 
  ↓
AI Agent selects: Get Sales Orders tool
  ↓
HTTP Request to S/4HANA
  ↓
Returns JSON data
  ↓
AI formats and presents
```

### When You Ask About Documents:
```
"What's in the invoice PDF?"
  ↓
AI Agent selects: Document Knowledge Base tool
  ↓
Question → OpenAI Embeddings → Vector [0.123, -0.456, ...]
  ↓
Qdrant searches for similar vectors
  ↓
Returns top 5 most relevant document chunks
  ↓
AI reads chunks and answers your question
```

## 🔧 Troubleshooting

### Issue: "No documents found in vector search"

**Solution:**
1. Check Qdrant has documents:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:6333/collections/s4hana-documents"
   ```
2. If vectors_count = 0, run the indexer workflow again
3. Make sure the PO numbers you're using have actual attachments

### Issue: "Document indexer fails at 'Get Document Metadata'"

**Possible causes:**
- PO numbers don't exist in S/4HANA
- Those POs don't have attachments
- Document service requires different object keys

**Solution:**
1. Test the attachment service manually:
   ```powershell
   curl.exe -k -u s4gui4:Sap@123456 `
     "https://49.206.196.74:8009/sap/opu/odata/sap/CV_ATTACHMENT_SRV/DocumentHeaderSet?`$format=json&`$filter=ObjectKey eq '4500000000'"
   ```
2. If it returns empty results, those POs have no attachments
3. Try different PO numbers

### Issue: "PDF extraction failed"

**Cause:** The PDF is a scanned image (not text-based)

**Solution:**
- Use text-based PDFs only for now
- For scanned PDFs, you'd need OCR (not included in basic n8n)

### Issue: "AI not using Document Knowledge Base tool"

**Solution:**
1. Make your question explicitly about documents:
   - Good: "What's in the PDF?"
   - Good: "What does the invoice document say?"
   - Bad: "Show me invoice data" (will use structured tool)
2. Check that Qdrant has documents indexed

## 📊 Checking What's Indexed

### See total document count:
```powershell
Invoke-RestMethod -Uri "http://localhost:6333/collections/s4hana-documents" |
  Select-Object -ExpandProperty result |
  Select-Object points_count, vectors_count, indexed_vectors_count
```

### Search for a specific document:
```powershell
$body = @{
  query = @{
    must = @(
      @{
        key = "businessObject"
        match = @{ value = "4500000000" }
      }
    )
  }
  limit = 10
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:6333/collections/s4hana-documents/points/search" `
  -ContentType "application/json" `
  -Body $body
```

## 🎓 Advanced: Adding More Documents

### To index more PO/Invoice types:

1. Open indexer workflow
2. Update "Set Business Objects" node:
   ```json
   {
     "purchaseOrders": ["4500000000", "4500000001", "4500000002", "4500000003"],
     "invoices": ["1000", "4900000000", "1001", "1002"]
   }
   ```
3. Execute workflow
4. Check Qdrant vectors increased

### To schedule automatic indexing:

1. Replace "Manual Trigger" with "Schedule Trigger"
2. Set schedule: Daily at 2:00 AM
3. Activate workflow
4. Documents will auto-index every day

## ✅ Success Criteria

You know it's working when:

1. ✅ Chat responds to "Show me sales orders" (structured data)
2. ✅ Qdrant shows vectors_count > 0
3. ✅ Chat responds to "What documents are attached to PO X?" (RAG search)
4. ✅ AI cites which tool it used (Get Sales Orders vs Document Knowledge Base)
5. ✅ Follow-up questions work (memory active)

## 📞 Quick Commands Reference

### Qdrant Management:
```powershell
# Check status
docker ps | Select-String qdrant

# View collection stats
Invoke-RestMethod -Uri "http://localhost:6333/collections/s4hana-documents"

# Restart Qdrant
docker restart qdrant

# View logs
docker logs qdrant
```

### Testing S/4HANA Services:
```powershell
# Test sales service
curl.exe -k -u s4gui4:Sap@123456 "https://49.206.196.74:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view?`$format=json&`$top=3"

# Test purchase service
curl.exe -k -u s4gui4:Sap@123456 "https://49.206.196.74:8009/sap/opu/odata/sap/C_PURCHASEORDER_FS_SRV/C_PurchaseOrderFs?`$format=json&`$top=3"

# Test attachment service
curl.exe -k -u s4gui4:Sap@123456 "https://49.206.196.74:8009/sap/opu/odata/sap/CV_ATTACHMENT_SRV/DocumentHeaderSet?`$format=json&`$top=3"
```

## 🎉 You're All Set!

Your RAG system is ready to use:
- 3 structured data tools (Sales, Purchase, Financial)
- 1 document search tool (RAG with Qdrant)
- Persistent vector storage
- Conversational memory
- No external dependencies except OpenAI

**Start chatting and enjoy your AI-powered S/4HANA assistant!** 🚀
