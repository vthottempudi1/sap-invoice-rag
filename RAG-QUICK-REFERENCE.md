# RAG System - Quick Reference Card

## 🚀 Quick Start (Choose Your Path)

### Path 1: Pinecone (Managed, Cloud) - 45 min
```
1. Sign up: https://www.pinecone.io/
2. Create index: s4hana-documents, 1536 dims, cosine
3. Import: n8n-s4hana-document-indexer.json
4. Import: n8n-S4HANA-OpenAI-RAG-Complete.json
5. Run indexer → Test chat
```
**Cost:** Free 1 month, then $70/mo  
**Best for:** Production, managed

### Path 2: Qdrant (Self-Hosted, Free) - 20 min
```powershell
1. docker run -d -p 6333:6333 qdrant/qdrant
2. Invoke-RestMethod -Method PUT `
     -Uri "http://localhost:6333/collections/s4hana-documents" `
     -ContentType "application/json" `
     -Body '{"vectors":{"size":1536,"distance":"Cosine"}}'
3. Import workflows (use Qdrant nodes instead of Pinecone)
4. Run indexer → Test chat
```
**Cost:** Free forever  
**Best for:** Development, self-hosted

### Path 3: In-Memory (Testing) - 5 min
```
1. Import workflows
2. Replace Pinecone nodes with In-Memory Vector Store
3. Run indexer → Test chat
```
**Cost:** Free  
**Best for:** POC, testing  
⚠️ **Note:** Embeddings lost on restart

---

## 📁 Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `n8n-S4HANA-OpenAI-RAG-Complete.json` | Main chat workflow | Import to n8n, activate |
| `n8n-s4hana-document-indexer.json` | Document indexer | Run once to populate DB |
| `RAG-SETUP-COMPLETE-GUIDE.md` | Step-by-step setup | Read first for Pinecone |
| `RAG-ALTERNATIVE-VECTOR-STORES.md` | Other vector DBs | If not using Pinecone |
| `RAG-ARCHITECTURE-DIAGRAMS.md` | Visual diagrams | Understand architecture |
| `RAG-IMPLEMENTATION-SUMMARY.md` | Overview | Start here |

---

## 🔧 Configuration Checklist

### Credentials Needed:
- ✅ SAP S/4HANA Basic Auth (you have this)
- ✅ OpenAI API (you have this)
- ⬜ Pinecone API (or)
- ⬜ Qdrant connection (local)

### Workflow Setup:
1. ⬜ Import document indexer workflow
2. ⬜ Update credential IDs in all nodes
3. ⬜ Set business object IDs (PO/Invoice numbers)
4. ⬜ Import chat workflow
5. ⬜ Update credential IDs
6. ⬜ Verify Pinecone/Qdrant connection

### Testing:
1. ⬜ Run indexer workflow (should succeed)
2. ⬜ Check vector database (vectors created?)
3. ⬜ Activate chat workflow
4. ⬜ Test structured query: "Show me sales orders"
5. ⬜ Test document query: "What documents are attached to PO X?"

---

## 💬 Example Queries

### Structured Data (Existing Capability)
```
✅ "Show me sales orders"
✅ "Get purchase order 4500000000"
✅ "List financial documents from January 2024"
```

### Document Search (NEW RAG Capability)
```
🆕 "What documents are attached to PO 4500000000?"
🆕 "What does the invoice PDF say about payment terms?"
🆕 "Find documents mentioning 'delivery schedule'"
🆕 "Summarize the attachment for invoice 1000"
```

### Hybrid Queries (NEW)
```
🆕 "Show me PO 4500000000 and summarize its attachments"
🆕 "Compare invoice amount vs PDF content"
🆕 "Get financial docs and check their PDFs for payment dates"
```

---

## 🔍 Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Pinecone index not found" | Verify index name is `s4hana-documents` |
| "No documents in search" | Run indexer workflow first |
| "Document download failed" | Check PO/Invoice numbers are valid |
| "PDF extraction failed" | Ensure PDF is text-based (not scanned) |
| "AI not using doc tool" | Ask explicitly: "What's in the PDF?" |
| "Qdrant connection failed" | Check Docker: `docker ps | grep qdrant` |
| "Embeddings cost too high" | Reduce chunk size, index fewer docs |

---

## 📊 Performance & Costs

### Indexing Performance
- 1 document: ~2-3 seconds
- 100 documents: ~5-10 minutes
- 1000 documents: ~1-2 hours

### Query Response Times
- Structured query: ~1-2 seconds
- Document search: ~2-3 seconds
- Hybrid query: ~3-5 seconds

### OpenAI Costs (Monthly)
- 100 queries/day: ~$3-5/month
- 500 queries/day: ~$15-25/month
- Initial indexing (1000 docs): ~$0.10 one-time

### Vector Database Costs
- Pinecone: Free 1 month → $70/month
- Qdrant: Free (self-hosted)
- Supabase: Free tier → $25/month

---

## 🎯 Which Vector Store Should I Use?

```
┌─────────────────────────────────────────────┐
│ Do you want managed cloud service?          │
│   ├─ Yes → Pinecone ($70/mo)               │
│   └─ No → Next question                     │
│                                             │
│ Are you okay with self-hosting?            │
│   ├─ Yes → Qdrant (Free, Docker)          │
│   └─ No → Supabase ($25/mo, managed)      │
│                                             │
│ Just testing/learning?                     │
│   └─ In-Memory (Free, non-persistent)     │
└─────────────────────────────────────────────┘
```

**My Recommendation:** Start with Qdrant (free, persistent, easy upgrade path)

---

## 🛠️ Common Commands

### Qdrant Docker
```powershell
# Start Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

# Check status
docker ps | Select-String qdrant

# Create collection
Invoke-RestMethod -Method PUT `
  -Uri "http://localhost:6333/collections/s4hana-documents" `
  -ContentType "application/json" `
  -Body '{"vectors":{"size":1536,"distance":"Cosine"}}'

# Verify collection
Invoke-RestMethod -Uri "http://localhost:6333/collections/s4hana-documents"

# Stop Qdrant
docker stop qdrant

# Remove Qdrant
docker rm qdrant
```

### Pinecone CLI
```powershell
# Install Pinecone CLI
pip install pinecone-client

# List indexes
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='YOUR_KEY'); print(pc.list_indexes())"

# Get index stats
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='YOUR_KEY'); idx = pc.Index('s4hana-documents'); print(idx.describe_index_stats())"
```

---

## 📈 Scaling Recommendations

### Small (<1000 docs)
- Vector DB: Qdrant (Docker) or In-Memory
- n8n: Single instance
- Works great, low cost

### Medium (1000-10,000 docs)
- Vector DB: Qdrant or Supabase
- n8n: Multiple workers
- Consider scheduled indexing

### Large (>10,000 docs)
- Vector DB: Pinecone or Qdrant Cloud
- n8n: Cluster with Redis
- Auto-scheduled indexing
- Load balancing

---

## 🔐 Security Notes

### Current Setup:
- S/4HANA: Basic Auth (credentials stored in n8n)
- OpenAI: API key (credentials stored in n8n)
- Vector DB: API key (credentials stored in n8n)

### Production Recommendations:
1. Use n8n's credential encryption
2. Rotate API keys regularly
3. Implement user authentication
4. Add document-level permissions
5. Use HTTPS for all connections
6. Enable audit logging

---

## 📚 Documentation Links

- **n8n Docs:** https://docs.n8n.io/
- **LangChain Docs:** https://docs.langchain.com/
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings
- **Pinecone:** https://docs.pinecone.io/
- **Qdrant:** https://qdrant.tech/documentation/
- **SAP OData:** https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE

---

## ✅ Success Criteria

You'll know it's working when:
1. ✅ Indexer workflow completes without errors
2. ✅ Vector database shows vector count > 0
3. ✅ Chat workflow responds to structured queries
4. ✅ Chat workflow responds to document queries
5. ✅ AI cites document sources in responses
6. ✅ Follow-up questions work (memory active)

---

## 🆘 Get Help

**Question?** Check these in order:
1. `RAG-IMPLEMENTATION-SUMMARY.md` - Overview
2. `RAG-SETUP-COMPLETE-GUIDE.md` - Detailed setup
3. `RAG-ALTERNATIVE-VECTOR-STORES.md` - Vector DB options
4. `RAG-ARCHITECTURE-DIAGRAMS.md` - How it works

**Still stuck?** Common issues:
- Credential IDs not updated → Update in workflow JSON
- Vector DB not running → Check Docker or Pinecone dashboard
- Documents not indexed → Run indexer workflow first
- AI not using tool → Ask explicitly about documents

---

## 🎉 Next Steps After Setup

1. **Index Your Documents:**
   - Update business object IDs in indexer
   - Run indexer workflow
   - Verify in vector database

2. **Test Queries:**
   - Try 3 structured queries (should work as before)
   - Try 3 document queries (new capability)
   - Try 2 hybrid queries (combination)

3. **Schedule Indexing:**
   - Change manual trigger to schedule trigger
   - Set to run daily at 2 AM
   - Keeps document knowledge fresh

4. **Monitor & Optimize:**
   - Check OpenAI usage dashboard
   - Monitor vector database size
   - Adjust chunk size if needed
   - Add more document types

5. **Scale:**
   - Add more business objects
   - Index additional document services
   - Implement user permissions
   - Add analytics

---

**Ready?** → Start with `RAG-SETUP-COMPLETE-GUIDE.md`  
**Questions?** → I'm here to help!
