"""
FastAPI Server for SAP Invoice RAG System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

from sap_invoice_rag import (
    query_invoices,
    get_invoice_count,
    get_invoices_by_date_range
)

# Initialize FastAPI app
app = FastAPI(
    title="SAP Invoice RAG API",
    description="Query SAP invoices using natural language",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"

class QueryResponse(BaseModel):
    answer: str
    session_id: str

class DateRangeRequest(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD

class InvoiceCountResponse(BaseModel):
    total_count: int

class HealthResponse(BaseModel):
    status: str
    message: str


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "SAP Invoice RAG API is running"
    }

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Query invoices using natural language
    
    Example:
    ```
    {
        "question": "How many invoices in 2024?",
        "session_id": "user123"
    }
    ```
    """
    try:
        answer = query_invoices(request.question, request.session_id)
        return {
            "answer": answer,
            "session_id": request.session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/count", response_model=InvoiceCountResponse)
async def count_endpoint():
    """Get total count of unique invoices"""
    try:
        count = get_invoice_count()
        return {"total_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/invoices/date-range")
async def date_range_endpoint(request: DateRangeRequest):
    """
    Get invoices within a date range
    
    Example:
    ```
    {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    ```
    """
    try:
        invoices = get_invoices_by_date_range(
            request.start_date,
            request.end_date
        )
        return {
            "count": len(invoices),
            "invoices": invoices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
