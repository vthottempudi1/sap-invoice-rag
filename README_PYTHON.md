# SAP Invoice RAG System - Python Implementation

Complete Python implementation of the SAP Invoice RAG system using LangChain, OpenAI, and Pinecone.

## Features

✅ **Automatic Deduplication**: Handles invoice chunks by deduplicating on ID field  
✅ **Date Conversion**: Converts SAP `/Date(timestamp)/` format to `YYYY-MM-DD`  
✅ **Date Range Filtering**: Query invoices within specific date ranges  
✅ **AI Agent**: Uses GPT-4o-mini with LangChain for intelligent queries  
✅ **Chat History**: Maintains conversation context across queries  
✅ **Vector Search**: Pinecone vector database with OpenAI embeddings  
✅ **Flexible Indexing**: Index from JSON files with automatic chunking  

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your-openai-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
```

Or set them in your shell:

```bash
# PowerShell
$env:OPENAI_API_KEY="your-openai-api-key"
$env:PINECONE_API_KEY="your-pinecone-api-key"

# Bash
export OPENAI_API_KEY="your-openai-api-key"
export PINECONE_API_KEY="your-pinecone-api-key"
```

### 3. Configure Settings

Edit the configuration in both scripts:

**sap_invoice_indexer.py:**
```python
PINECONE_INDEX = "n8n-s4hana-new"
PINECONE_NAMESPACE = "invoice-documents"
PINECONE_ENVIRONMENT = "us-east-1"  # Update with your region
```

**sap_invoice_rag.py:**
```python
PINECONE_INDEX = "n8n-s4hana-new"
PINECONE_NAMESPACE = "invoice-documents"
```

## Usage

### Indexing Invoices

Index invoice data from a JSON file to Pinecone:

```bash
# Index invoices from JSON file
python sap_invoice_indexer.py --file invoices.json

# Clear namespace before indexing
python sap_invoice_indexer.py --file invoices.json --clear

# Index without chunking (one vector per invoice)
python sap_invoice_indexer.py --file invoices.json --no-chunk

# Show index statistics
python sap_invoice_indexer.py --stats
```

**Expected JSON format:**

```json
[
  {
    "invoiceNumber": "1000",
    "companyCode": "AB1",
    "fiscalYear": "2020",
    "documentDate": "/Date(1609113600000)/",
    "postingDate": "/Date(1609200000000)/",
    "amount": 15000,
    "currency": "USD",
    "documentType": "DR",
    "businessArea": "Sales",
    "reference": "PO-12345"
  }
]
```

### Querying Invoices

Run the RAG system for interactive queries:

```bash
python sap_invoice_rag.py
```

**Example queries:**

```
You: How many total invoices are there?
Assistant: There are 32 unique invoices in the database (retrieved from 70 chunks).

You: Show me invoices from 2020 to 2021
Assistant: I found 15 invoices between 2020-01-01 and 2021-12-31...

You: What's the total amount for company code AB1?
Assistant: Company code AB1 has 12 invoices totaling $125,450.00 USD.

You: List invoices over $10,000
Assistant: Here are the invoices over $10,000:
1. Invoice 1000: $15,000 USD (2020-12-28)
...
```

### Programmatic Usage

Use the functions directly in your code:

```python
from sap_invoice_rag import query_invoices, get_invoice_count, get_invoices_by_date_range

# Get total count
count = get_invoice_count()
print(f"Total invoices: {count}")

# Query with AI
response = query_invoices("Show me invoices from January 2024")
print(response)

# Get invoices by date range
invoices = get_invoices_by_date_range("2020-01-01", "2021-12-31")
for inv in invoices:
    print(f"{inv['invoiceNumber']}: {inv['amount']} {inv['currency']}")
```

## Architecture

### Key Components

1. **OpenAI Embeddings** (`text-embedding-3-small`, 512 dimensions)
2. **Pinecone Vector Store** (Serverless, cosine similarity)
3. **LangChain Agent** (GPT-4o-mini with tools)
4. **Chat Memory** (Window buffer, 20 messages)

### Data Flow

```
User Query
    ↓
AI Agent (GPT-4o-mini)
    ↓
Search Tool
    ↓
Pinecone Retrieval (k=200)
    ↓
Deduplication (by ID field)
    ↓
Date Conversion (SAP → YYYY-MM-DD)
    ↓
AI Response
```

### Deduplication Logic

Each invoice may be stored as multiple chunks in Pinecone. The system:

1. Retrieves all matching chunks (topK=200)
2. Extracts the `ID` field from each chunk (format: `invoice_1000_AB1_2020`)
3. Deduplicates by ID using a dictionary
4. Returns only unique invoices
5. AI agent counts unique IDs for accurate totals

## Troubleshooting

### Issue: "No invoices found"

**Solution:** Check Pinecone connection and namespace:
```bash
python sap_invoice_indexer.py --stats
```

### Issue: Wrong invoice counts

**Solution:** Verify deduplication is working:
```python
from sap_invoice_rag import retriever, deduplicate_invoices

docs = retriever.get_relevant_documents("invoice")
print(f"Total chunks: {len(docs)}")

unique = deduplicate_invoices(docs)
print(f"Unique invoices: {len(unique)}")
```

### Issue: Dates not converting

**Solution:** Check SAP date format in your data:
```python
from sap_invoice_rag import convert_sap_date

date_str = "/Date(1609113600000)/"
converted = convert_sap_date(date_str)
print(f"Converted: {converted}")  # Should output: 2020-12-28
```

### Issue: Import errors

**Solution:** Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## Configuration Options

### Embedding Models

Change embedding model in both scripts:

```python
# Current: text-embedding-3-small (512 dims)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=512,
    api_key=OPENAI_API_KEY
)

# Alternative: text-embedding-3-large (higher quality)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=1024,
    api_key=OPENAI_API_KEY
)
```

**Note:** If changing dimensions, recreate the Pinecone index.

### Chat Model

Change LLM in `sap_invoice_rag.py`:

```python
# Current: GPT-4o-mini
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=OPENAI_API_KEY
)

# Alternative: GPT-4
llm = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=0.3,
    api_key=OPENAI_API_KEY
)
```

### Retrieval Settings

Adjust retrieval in `sap_invoice_rag.py`:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 200,  # Number of chunks to retrieve
        "filter": {"companyCode": "AB1"}  # Optional metadata filter
    }
)
```

### Chunking Strategy

Adjust chunking in `sap_invoice_indexer.py`:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Maximum characters per chunk
    chunk_overlap=100,  # Overlap between chunks
    separators=["\n\n", "\n", " ", ""]
)
```

## Performance Notes

- **Indexing**: ~32 invoices = 70 chunks (with default settings)
- **Retrieval**: topK=200 ensures all invoices captured
- **Deduplication**: O(n) time complexity, efficient for thousands of chunks
- **Chat History**: Limited to 20 messages to manage context window

## API Costs (Estimate)

Per 1000 queries (assuming 32 invoices, 70 chunks):

- **Embeddings**: $0.02 (text-embedding-3-small)
- **Chat Model**: $1.50 (gpt-4o-mini, ~500 tokens/query)
- **Pinecone**: $0.096/hour (serverless, minimal usage)

**Total**: ~$1.52 per 1000 queries + minimal Pinecone costs

## Next Steps

1. **Web Interface**: Add Flask/FastAPI for REST API
2. **Batch Processing**: Index multiple JSON files at once
3. **Advanced Filters**: Add filters for amount ranges, document types
4. **Export**: Add CSV/Excel export functionality
5. **Visualization**: Create charts for invoice analytics
6. **Streaming**: Add streaming responses for long queries

## License

MIT License - Use freely for commercial and personal projects.

## Support

For issues or questions, create an issue in the repository or contact the maintainer.
