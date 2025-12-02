# SAP Invoice RAG System

AI-powered SAP invoice query system using LangChain, Pinecone, and OpenAI.

## Features

- 🤖 Natural language invoice queries
- 🔍 Semantic search with Pinecone vector database
- 📊 Automatic deduplication and date conversion
- 💬 Chat interface with conversation history
- 📈 FastAPI REST API
- 🎨 Streamlit web interface

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key
- Pinecone API key

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/sap-invoice-rag.git
cd sap-invoice-rag

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_api.txt
```

### Configuration

Create `.env` file:

```env
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
```

### Run Locally

**Terminal 1 - API Server:**
```bash
python api_server.py
```

**Terminal 2 - Streamlit App:**
```bash
streamlit run streamlit_app.py
```

Access at http://localhost:8501

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository
5. Set main file: `streamlit_app.py`
6. Add secrets (Settings → Secrets):
   ```toml
   OPENAI_API_KEY = "your-key"
   PINECONE_API_KEY = "your-key"
   ```
7. Deploy!

### Deploy API to Railway/Render

See [README_DEPLOYMENT.md](README_DEPLOYMENT.md) for detailed instructions.

## Project Structure

```
├── sap_invoice_rag.py       # Core RAG system
├── api_server.py            # FastAPI backend
├── streamlit_app.py         # Web interface
├── sap_invoice_indexer.py   # Index invoices to Pinecone
├── requirements.txt         # Core dependencies
├── requirements_api.txt     # API dependencies
└── .env                     # API keys (not in git)
```

## Usage

### Python Script
```python
from sap_invoice_rag import query_invoices

answer = query_invoices("How many invoices in 2024?")
print(answer)
```

### API
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How many invoices?", "session_id": "user1"}'
```

### Web Interface
- Chat with your invoices
- Filter by date range
- Export to CSV

## License

MIT
