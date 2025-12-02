# SAP Invoice RAG - FastAPI & Streamlit Deployment

## 📁 Files Created

1. **api_server.py** - FastAPI backend server
2. **streamlit_app.py** - Streamlit web interface
3. **requirements_api.txt** - Additional dependencies

## 🚀 Deployment Steps

### Step 1: Install Dependencies

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install new packages
pip install -r requirements_api.txt
```

### Step 2: Start FastAPI Server

```powershell
# Run in Terminal 1
python api_server.py
```

The API will start at: **http://localhost:8000**

**API Documentation**: http://localhost:8000/docs (automatic Swagger UI)

### Step 3: Start Streamlit App

```powershell
# Run in Terminal 2
streamlit run streamlit_app.py
```

The Streamlit app will open at: **http://localhost:8501**

## 📡 API Endpoints

### 1. Health Check
```
GET http://localhost:8000/
```

### 2. Query Invoices (Natural Language)
```
POST http://localhost:8000/query
Content-Type: application/json

{
  "question": "How many invoices in 2024?",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "answer": "There are 28 invoices in fiscal year 2024.",
  "session_id": "user123"
}
```

### 3. Get Total Count
```
GET http://localhost:8000/count
```

**Response:**
```json
{
  "total_count": 32
}
```

### 4. Query by Date Range
```
POST http://localhost:8000/invoices/date-range
Content-Type: application/json

{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

## 🎨 Streamlit Features

### Chat Assistant Tab
- Interactive chat interface
- Session-based conversation history
- Natural language queries
- Real-time responses from OpenAI

### Date Range Query Tab
- Filter invoices by date range
- View results in table format
- Download results as CSV
- Pandas DataFrame display

### Sidebar Features
- API connection status
- Total invoice count
- Session ID display
- Clear chat history
- Example queries

## 🧪 Test the API

### Using curl:

```powershell
# Health check
curl http://localhost:8000/

# Query invoices
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d '{"question": "How many invoices?", "session_id": "test"}'

# Get count
curl http://localhost:8000/count

# Date range query
curl -X POST http://localhost:8000/invoices/date-range `
  -H "Content-Type: application/json" `
  -d '{"start_date": "2024-01-01", "end_date": "2024-12-31"}'
```

### Using Python requests:

```python
import requests

# Query endpoint
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "Show me invoices with company code MF01",
        "session_id": "python_client"
    }
)
print(response.json()["answer"])
```

## 🌐 Production Deployment

### Option 1: Deploy to Cloud (Railway/Render/Heroku)

1. Add `Procfile`:
```
web: uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

2. Push to Git repository
3. Connect to Railway/Render
4. Add environment variables:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`

### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements_api.txt ./
RUN pip install -r requirements_api.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```powershell
docker build -t sap-invoice-api .
docker run -p 8000:8000 --env-file .env sap-invoice-api
```

### Option 3: Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Deploy from GitHub repository
4. Add secrets (Settings → Secrets):
   ```toml
   OPENAI_API_KEY = "your-key"
   PINECONE_API_KEY = "your-key"
   ```

**Note**: For Streamlit Cloud, modify `streamlit_app.py` to call the RAG functions directly instead of API:

```python
# Replace API calls with:
from sap_invoice_rag import query_invoices
answer = query_invoices(user_question, st.session_state.session_id)
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **CORS**: Update `allow_origins` in production:
   ```python
   allow_origins=["https://your-streamlit-app.com"]
   ```
3. **API Authentication**: Add API key authentication:
   ```python
   from fastapi.security import APIKeyHeader
   
   api_key_header = APIKeyHeader(name="X-API-Key")
   
   @app.post("/query")
   async def query_endpoint(request: QueryRequest, api_key: str = Depends(api_key_header)):
       if api_key != os.getenv("API_KEY"):
           raise HTTPException(status_code=403, detail="Invalid API Key")
       # ... rest of code
   ```

## 📊 Monitoring & Logging

Add logging to `api_server.py`:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    logger.info(f"Query received: {request.question}")
    # ... rest of code
```

## 🐛 Troubleshooting

### API not starting?
- Check if port 8000 is available: `netstat -ano | findstr :8000`
- Verify `.env` file exists with API keys

### Streamlit can't connect to API?
- Ensure API server is running
- Check `API_URL` in `streamlit_app.py` matches your setup

### Import errors?
- Activate virtual environment
- Install all dependencies: `pip install -r requirements_api.txt`

## 📈 Performance Tips

1. **Caching**: Add Streamlit caching:
   ```python
   @st.cache_data(ttl=300)
   def get_invoice_count():
       response = requests.get(f"{API_URL}/count")
       return response.json()["total_count"]
   ```

2. **Async Processing**: For large queries, use background tasks

3. **Database**: Consider caching Pinecone results in Redis

## 🎯 Next Steps

- [ ] Add user authentication
- [ ] Implement rate limiting
- [ ] Add more visualization charts
- [ ] Export reports (PDF/Excel)
- [ ] Email notifications
- [ ] Webhook integrations
