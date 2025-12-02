# Step-by-Step Workflow Execution Guide

## 📋 Complete Guide to Running Your Invoice RAG System

This guide provides detailed, step-by-step instructions for executing both workflows in your invoice RAG system.

---

## 🎯 Overview: Two Workflows to Execute

| Workflow | Purpose | When to Run | Execution Time |
|----------|---------|-------------|----------------|
| **n8n-S4HANA-Invoice-RAG.json** | Chat interface for asking questions | Always active (on-demand) | Instant responses |
| **n8n-invoice-document-indexer.json** | Index invoice PDFs into Pinecone | Once initially, then periodically | 2-3 sec per invoice |

---

## 🚀 PART 1: Setting Up Chat Workflow (One-Time Setup)

### Step 1.1: Open n8n Cloud

1. Open your web browser
2. Go to: **https://vthottempudi1.app.n8n.cloud**
3. Log in with your credentials
4. You'll see the n8n dashboard with your workflows

**Screenshot Reference**: You should see a list of existing workflows (if any).

---

### Step 1.2: Import the Chat Workflow

1. Click the **"Add workflow"** button (top-right corner)
   - It's a blue button with a "+" icon
   
2. From the dropdown menu, select **"Import from file"**

3. A file browser dialog will open

4. Navigate to your folder: `C:\Users\vthot\N8N-DOCKER-SAP-AGENTIC-AI`

5. Select the file: **`n8n-S4HANA-Invoice-RAG.json`**

6. Click **"Open"**

7. n8n will process the file and display the workflow

8. You'll see **8 nodes** appear on the canvas:
   ```
   - When chat message received (trigger node)
   - AI Agent (brain of the system)
   - OpenAI Chat Model (GPT-4o-mini)
   - Window Buffer Memory (conversation context)
   - Get Financial Documents (HTTP request tool)
   - Pinecone Vector Store (vector database)
   - Vector Store Retriever (search tool)
   - OpenAI Embeddings (text-to-vector converter)
   ```

9. Click **"Save"** button (top-right)

10. Give it a name: **"Invoice RAG Chat"** (or keep default name)

---

### Step 1.3: Configure Pinecone Credential (Critical Step!)

Before activating, you need to link the Pinecone credential:

1. In the workflow canvas, click on the **"Pinecone Vector Store"** node
   - It's the 6th node in the workflow

2. You'll see a credential dropdown that says `"Pinecone Invoice API"`

3. Click the dropdown → Select **"Create New Credential"**

4. A credential form will appear:
   ```
   Name: Pinecone Invoice API
   API Key: [Enter your Pinecone API key here]
   Environment: [Your Pinecone environment, e.g., "us-east1-gcp"]
   ```

5. **To get your Pinecone API key**:
   - Open new tab: https://app.pinecone.io
   - Log in with: vthottempudi1@gmail.com
   - Go to **"API Keys"** section (left sidebar)
   - Copy your API key
   - Go to **"Indexes"** section
   - If `n8n-s4hana` index doesn't exist, create it:
     - Click **"Create Index"**
     - Name: `n8n-s4hana`
     - Dimensions: `1536`
     - Metric: `Cosine`
     - Click **"Create"**

6. Paste the API key in n8n credential form

7. Click **"Save"** (in credential dialog)

8. The Pinecone Vector Store node should now show a green checkmark ✓

9. Click **"Save"** (workflow save button, top-right)

---

### Step 1.4: Activate the Chat Workflow

1. Look at the **top-right corner** of the workflow canvas

2. You'll see a toggle switch labeled **"Inactive"** or **"Active"**

3. Click the toggle to turn it **ON (Active)**
   - The toggle will turn green/blue
   - A webhook URL will be generated

4. You'll see a success message: "Workflow activated"

5. The workflow is now **LIVE** and listening for chat messages!

---

### Step 1.5: Test the Chat Interface

#### Option A: Using n8n Chat Interface (Recommended)

1. In the workflow canvas, find the **"When chat message received"** node (first node)

2. Click on it to select it

3. Look for the **"Chat"** button (appears near the node or in the right panel)

4. Click **"Chat"** - a chat window will open

5. **Try these test queries** (one at a time):

   **Test 1: Structured Data (Works Immediately)**
   ```
   Type: "Show me all invoices"
   Press Enter
   ```
   
   **Expected Response**:
   - AI will use the "Get Financial Documents" tool
   - You'll see invoice data from S/4HANA
   - Response includes: invoice numbers, amounts, dates
   - Response time: 2-5 seconds
   
   **Example Response**:
   ```
   I found the following invoices from S/4HANA:
   
   1. Invoice 1000 - Amount: $5,000 - Date: 2024-01-15
   2. Invoice 4900000000 - Amount: $12,500 - Date: 2024-02-20
   3. Invoice 4900000001 - Amount: $8,300 - Date: 2024-03-10
   
   (Source: Financial Documents Tool - FAC_FINANCIAL_DOCUMENT_SRV_01)
   ```

   **Test 2: More Structured Queries**
   ```
   Type: "What invoices were posted this month?"
   Type: "Show me invoice amounts over $10,000"
   Type: "List all financial documents"
   ```

   **Test 3: Document Content (Will fail until indexing - that's expected!)**
   ```
   Type: "What does invoice 1000 say about payment terms?"
   ```
   
   **Expected Response** (before indexing):
   ```
   I don't have access to the content of invoice documents yet. 
   The Invoice Document Knowledge Base is empty. You need to run 
   the document indexer workflow first to populate it with invoice PDFs.
   ```

6. **Verify Chat is Working**:
   - ✅ AI responds to questions
   - ✅ AI uses "Get Financial Documents" tool for structured queries
   - ✅ Responses include invoice data from S/4HANA
   - ✅ AI mentions which tool was used
   - ✅ Follow-up questions work (memory retained)

#### Option B: Using Webhook URL (Advanced)

1. Go to workflow settings (gear icon)
2. Find the webhook URL (something like: `https://vthottempudi1.app.n8n.cloud/webhook/ae886090-...`)
3. Use Postman or curl to send POST requests with chat messages

---

## 📄 PART 2: Running the Document Indexer Workflow

This workflow indexes invoice PDFs into Pinecone so the chat can search document content.

### Step 2.1: Import the Indexer Workflow

1. Go back to n8n dashboard (click "n8n" logo top-left)

2. Click **"Add workflow"** button again

3. Select **"Import from file"**

4. Navigate to: `C:\Users\vthot\N8N-DOCKER-SAP-AGENTIC-AI`

5. Select: **`n8n-invoice-document-indexer.json`**

6. Click **"Open"**

7. The workflow will load with **12 nodes**:
   ```
   1. Manual Trigger
   2. Set Invoice Numbers
   3. Split Invoices
   4. Loop Invoices
   5. Get Invoice Document Metadata
   6. Flatten Document List
   7. Filter PDFs Only
   8. Download Invoice PDF Content
   9. Extract Invoice PDF Text
   10. Split Text into Chunks
   11. Store in Pinecone
   12. OpenAI Embeddings
   ```

8. Click **"Save"**

9. Name it: **"Invoice Document Indexer"**

---

### Step 2.2: Configure Pinecone Credential in Indexer

1. Click on the **"Store in Pinecone"** node (node #11)

2. In the credential dropdown, select the **same Pinecone credential** you created earlier:
   - Select: "Pinecone Invoice API"

3. If it doesn't appear, create it again using the same API key from Step 1.3

4. Verify these settings in the node:
   ```
   Mode: insert
   Index: n8n-s4hana
   Namespace: invoice-documents
   ```

5. Click **"Save"** (workflow save button)

---

### Step 2.3: Get Real Invoice Numbers from Your System

**Important**: You need invoice numbers that actually have PDF attachments!

#### Method 1: Ask the Chat (Recommended)

1. Go back to your **Invoice RAG Chat** workflow

2. Open the chat interface

3. Ask:
   ```
   "Show me all invoices"
   ```

4. Copy the invoice numbers from the response

5. Write them down or keep them in a text file

**Example Output**:
```
Invoice Numbers to Use:
- 1000
- 4900000000
- 4900000001
- 4900000002
```

#### Method 2: Test Manually (Advanced)

Open PowerShell and run:

```powershell
curl.exe -k -u s4gui4:Sap@123456 `
  "https://49.206.196.74:8009/sap/opu/odata/sap/FAC_FINANCIAL_DOCUMENT_SRV_01/Headers?`$format=json&`$top=10"
```

Look for invoice numbers in the response.

---

### Step 2.4: Update Invoice Numbers in Indexer

1. In the **Invoice Document Indexer** workflow, click on the **"Set Invoice Numbers"** node (node #2)

2. The right panel will show the node configuration

3. You'll see a JSON editor with:
   ```json
   {
     "invoices": ["1000", "4900000000", "4900000001", "4900000002"]
   }
   ```

4. **Replace these with YOUR invoice numbers**:
   ```json
   {
     "invoices": ["YOUR_INVOICE_1", "YOUR_INVOICE_2", "YOUR_INVOICE_3"]
   }
   ```

   **Example** (if you got invoices 1000, 2000, 3000):
   ```json
   {
     "invoices": ["1000", "2000", "3000"]
   }
   ```

5. Click **"Save"** (workflow save button)

**Important Notes**:
- Use invoice numbers that have PDF attachments
- Keep the JSON format exactly as shown (with quotes and square brackets)
- You can add as many invoice numbers as you want
- Start with 3-5 invoices for testing

---

### Step 2.5: Execute the Indexer Workflow (The Main Event!)

Now we'll actually run the indexer to populate Pinecone:

1. Make sure you're in the **Invoice Document Indexer** workflow

2. Look at the **top-right corner** - find the **"Execute Workflow"** button
   - It looks like a "Play" icon ▶️
   - Also called "Test Workflow"

3. Click **"Execute Workflow"**

4. **Watch the execution flow**:

   **What You'll See** (in real-time):

   ```
   Step 1: Manual Trigger fires
   ├─ Green checkmark appears ✓
   
   Step 2: Set Invoice Numbers executes
   ├─ Outputs array: ["1000", "2000", "3000"]
   ├─ Green checkmark ✓
   
   Step 3: Split Invoices
   ├─ Creates 3 separate branches (one per invoice)
   ├─ Green checkmark ✓
   ├─ Shows "3 items" in output
   
   Step 4-11: For EACH invoice (parallel execution):
   
   Invoice 1000:
   ├─ Loop Invoices → Sets currentInvoice = "1000" ✓
   ├─ Get Invoice Document Metadata → Calls SAP API ✓
   │   └─ Response: [{FileName: "Invoice_1000.pdf", MimeType: "application/pdf"}]
   ├─ Flatten Document List ✓
   ├─ Filter PDFs Only ✓
   │   └─ Keeps only PDFs, filters out Word/Excel
   ├─ Download Invoice PDF Content → Downloads binary file ✓
   │   └─ File size: ~500KB
   ├─ Extract Invoice PDF Text ✓
   │   └─ Text: "INVOICE #1000\nDate: 2024-01-15\nCustomer: ABC Corp..."
   ├─ Split Text into Chunks ✓
   │   └─ Creates 3 chunks (1000 chars each, 200 overlap)
   ├─ Store in Pinecone (with OpenAI Embeddings) ✓
   │   ├─ Chunk 1 → Embedding → Pinecone ✓
   │   ├─ Chunk 2 → Embedding → Pinecone ✓
   │   └─ Chunk 3 → Embedding → Pinecone ✓
   
   Invoice 2000: (same process)
   Invoice 3000: (same process)
   ```

5. **Monitor the execution**:
   - Green checkmarks ✓ = Success
   - Red X = Error (see troubleshooting section)
   - Orange = Running/In-progress
   - Gray = Not executed yet

6. **Execution will take**:
   - ~2-3 seconds per invoice
   - For 3 invoices: ~6-9 seconds total
   - For 10 invoices: ~20-30 seconds

7. **When execution completes**:
   - All nodes should be GREEN ✓
   - You'll see "Execution successful" message
   - Check the final node output to see vectors stored

---

### Step 2.6: Verify Indexing Was Successful

#### Method 1: Check n8n Execution Log

1. In the indexer workflow, look at the **"Store in Pinecone"** node output

2. Click on it and check the right panel

3. You should see output like:
   ```json
   {
     "success": true,
     "upsertedCount": 9,
     "namespace": "invoice-documents"
   }
   ```

4. `upsertedCount` = number of vectors added (chunks × invoices)

#### Method 2: Check Pinecone Dashboard

1. Open new browser tab: https://app.pinecone.io

2. Log in with: vthottempudi1@gmail.com

3. Click on index: **`n8n-s4hana`**

4. Look for namespace: **`invoice-documents`**

5. Check **"Vector Count"**:
   - Should be > 0
   - Example: 9 vectors (3 invoices × 3 chunks each)

6. If you see vectors, **SUCCESS!** ✅

#### Method 3: Test in Chat (Final Verification)

1. Go back to **Invoice RAG Chat** workflow

2. Open the chat interface

3. **Test document content queries**:

   ```
   Query 1: "What does invoice 1000 say about payment terms?"
   ```
   
   **Expected Response** (NOW it should work!):
   ```
   Invoice 1000 has payment terms of Net 30 days. The payment is 
   due on February 14, 2024. Late payments incur a 2% monthly penalty.
   
   (Source: Invoice Document Knowledge Base, file: Invoice_1000.pdf)
   ```

   ```
   Query 2: "Find invoices mentioning shipping costs"
   ```
   
   **Expected Response**:
   ```
   I found shipping information in invoice 2000. The shipping cost 
   was $150 for overnight delivery to New York.
   
   (Source: Invoice Document Knowledge Base)
   ```

   ```
   Query 3: "What line items are in invoice 1000?"
   ```
   
   **Expected Response**:
   ```
   Invoice 1000 contains the following line items:
   1. Product A - Qty: 10 - Price: $100 - Total: $1,000
   2. Product B - Qty: 5 - Price: $200 - Total: $1,000
   3. Shipping - $150
   Total: $2,150
   
   (Source: Invoice Document Knowledge Base, extracted from Invoice_1000.pdf)
   ```

4. **Verify RAG is working**:
   - ✅ AI provides specific content from PDFs
   - ✅ AI cites "Invoice Document Knowledge Base" as source
   - ✅ Answers include details not in structured data
   - ✅ File names are mentioned (e.g., "Invoice_1000.pdf")

---

## 🔄 PART 3: Re-Running the Indexer (Monthly/As Needed)

### When to Re-Run:

- New invoices created in S/4HANA
- Want to update existing invoice documents
- Added more invoice attachments

### How to Re-Run:

1. Open **Invoice Document Indexer** workflow

2. Click **"Set Invoice Numbers"** node

3. **Add new invoice numbers**:
   ```json
   {
     "invoices": ["OLD_1", "OLD_2", "NEW_1", "NEW_2", "NEW_3"]
   }
   ```

4. Click **"Save"**

5. Click **"Execute Workflow"** again

6. Wait for green checkmarks

7. New vectors will be added to Pinecone (existing ones remain)

**Pro Tip**: Use incremental indexing:
```json
{
  "invoices": ["NEW_INVOICE_1", "NEW_INVOICE_2"]
}
```
This adds only new invoices without re-processing old ones.

---

## 🎯 PART 4: Using Both Tools Together

### Example Combined Query:

**User asks in chat**:
```
"Show me invoices over $10,000 and tell me their payment terms"
```

**AI will**:
1. Use **Get Financial Documents** tool
   - Query SAP for invoices with amount > $10,000
   - Gets invoice numbers: 4900000000, 4900000001

2. Use **Invoice Document Knowledge Base** tool
   - Search Pinecone for payment terms in those specific invoices
   - Retrieves relevant PDF chunks

3. Combine both results:
   ```
   I found 2 invoices over $10,000:
   
   1. Invoice 4900000000 - $15,000 - Posted: 2024-02-20
      Payment Terms: Net 60 days, due March 21, 2024
      (From PDF: Invoice_4900000000.pdf)
   
   2. Invoice 4900000001 - $12,500 - Posted: 2024-03-10
      Payment Terms: 2/10 Net 30 (2% discount if paid within 10 days)
      (From PDF: Invoice_4900000001.pdf)
   
   Sources: Financial Documents Tool + Invoice Document Knowledge Base
   ```

---

## ⚠️ PART 5: Troubleshooting Execution Issues

### Issue 1: Indexer Shows "No documents found"

**Symptom**: Get Invoice Document Metadata returns empty array

**Cause**: Invoice numbers don't have attachments

**Solution**:
1. Test one invoice manually:
   ```powershell
   curl.exe -k -u s4gui4:Sap@123456 `
     "https://49.206.196.74:8009/sap/opu/odata/sap/CV_ATTACHMENT_SRV/DocumentHeaderSet?`$format=json&`$filter=ObjectKey eq '1000'"
   ```

2. Check response - should have `d.results` with documents

3. If empty, try different invoice numbers

4. Ask in chat: "Which invoices have attachments?"

---

### Issue 2: PDF Extraction Fails

**Symptom**: Extract Invoice PDF Text node shows error

**Cause**: Scanned PDF (image-based, not text)

**Solution**:
- Skip scanned PDFs for now (OCR not included)
- Use only text-based PDFs
- Check PDF by opening it - if you can select text, it will work

---

### Issue 3: Pinecone Connection Error

**Symptom**: "Store in Pinecone" node fails with 401 Unauthorized

**Cause**: Invalid API key or credential not linked

**Solution**:
1. Go to Pinecone credential settings
2. Verify API key is correct
3. Test API key in Pinecone dashboard
4. Re-enter and save
5. Re-execute workflow

---

### Issue 4: OpenAI Rate Limit

**Symptom**: "OpenAI Embeddings" fails with 429 error

**Cause**: Too many requests too fast

**Solution**:
- Wait 1 minute and retry
- Reduce number of invoices (index 5 at a time instead of 50)
- Check OpenAI usage dashboard for limits

---

### Issue 5: Execution Timeout

**Symptom**: Workflow stops mid-execution

**Cause**: n8n execution timeout (default 2 minutes)

**Solution**:
1. Go to workflow settings (gear icon)
2. Increase execution timeout to 10 minutes
3. Re-run workflow
4. Or index fewer invoices per run

---

## 📊 PART 6: Monitoring Execution Success

### Success Checklist After Each Run:

- [ ] Indexer execution completed (all green checkmarks)
- [ ] "Store in Pinecone" node shows `upsertedCount > 0`
- [ ] Pinecone dashboard shows vector count increased
- [ ] Chat responds to: "What does invoice X say about Y?"
- [ ] AI cites "Invoice Document Knowledge Base"
- [ ] Response includes PDF content (not just metadata)

### Execution Metrics to Track:

| Metric | How to Check | Good Value |
|--------|--------------|------------|
| **Vectors Added** | Pinecone dashboard | 3-5 per invoice |
| **Execution Time** | n8n execution log | 2-3 sec/invoice |
| **Success Rate** | Green checkmarks | 100% |
| **OpenAI Cost** | OpenAI usage dashboard | ~$0.01 per 100 invoices |
| **Chat Response Time** | Try queries | < 5 seconds |

---

## 🎓 PART 7: Advanced Execution Patterns

### Pattern 1: Scheduled Auto-Indexing

1. Open indexer workflow
2. Delete "Manual Trigger" node
3. Add "Schedule Trigger" node:
   - Trigger: Daily at 2:00 AM
   - OR: Weekly on Mondays
4. Connect to "Set Invoice Numbers"
5. Modify "Set Invoice Numbers" to fetch recent invoices dynamically
6. Activate workflow
7. Invoices auto-indexed daily!

### Pattern 2: Webhook-Triggered Indexing

1. Replace "Manual Trigger" with "Webhook" node
2. Accept invoice numbers as POST body
3. Chat workflow can trigger indexer with specific invoices
4. User asks: "Index invoice 5000"
5. Chat sends webhook request to indexer
6. Indexer processes invoice 5000 automatically

### Pattern 3: Batch Processing

For 100+ invoices:

1. Split into batches of 10
2. Run indexer 10 times (10 invoices each)
3. Avoids timeouts
4. Monitors progress after each batch

---

## 📝 Quick Reference: Execution Commands

### Run Chat Workflow:
```
1. Open: Invoice RAG Chat workflow
2. Ensure: Active toggle is ON (green)
3. Click: Chat button
4. Type: Your question
5. Press: Enter
6. Wait: 2-5 seconds for response
```

### Run Indexer Workflow:
```
1. Open: Invoice Document Indexer workflow
2. Update: Invoice numbers in "Set Invoice Numbers" node
3. Save: Workflow
4. Click: Execute Workflow button (▶️)
5. Watch: Execution progress (green checkmarks)
6. Verify: Pinecone dashboard shows new vectors
7. Test: Chat with document content queries
```

---

## 🎉 Success! You're Ready

You now know how to:

✅ Import workflows to n8n Cloud
✅ Configure Pinecone credentials
✅ Activate the chat workflow
✅ Test structured data queries (immediate)
✅ Run the document indexer
✅ Verify indexing success
✅ Test RAG document queries
✅ Troubleshoot execution issues
✅ Monitor execution metrics
✅ Re-run indexer for new invoices

**Next Steps**:
1. Execute both workflows following this guide
2. Test with your real invoice data
3. Refine invoice numbers based on results
4. Set up scheduled indexing (optional)
5. Start asking complex invoice questions!

---

## 🔗 Related Guides

- **Setup Guide**: `INVOICE-RAG-SETUP-GUIDE.md` (system architecture)
- **General RAG**: `HOW-TO-USE-RAG-SYSTEM.md` (broader S/4HANA RAG)
- **Quick Reference**: `RAG-QUICK-REFERENCE.md` (cheat sheet)

---

**Questions?** Ask the AI assistant in the chat workflow! 🤖

**Need help?** Check the troubleshooting sections in this guide or `INVOICE-RAG-SETUP-GUIDE.md`.
