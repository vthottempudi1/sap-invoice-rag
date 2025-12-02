# SAP Invoice RAG API - Docker Deployment Guide

## 🐳 Deploy FastAPI with Docker

### Option 1: Docker Compose (Recommended)

```powershell
# Build and start the API
docker-compose -f docker-compose-api.yml up -d

# View logs
docker-compose -f docker-compose-api.yml logs -f

# Stop the API
docker-compose -f docker-compose-api.yml down
```

API will be available at: `http://localhost:8000`

### Option 2: Docker Commands

```powershell
# Build the image
docker build -f Dockerfile.api -t sap-invoice-api .

# Run the container
docker run -d \
  --name sap-invoice-api \
  -p 8000:8000 \
  --env-file .env \
  sap-invoice-api

# View logs
docker logs -f sap-invoice-api

# Stop and remove
docker stop sap-invoice-api
docker rm sap-invoice-api
```

## 🔗 Integration with n8n

If n8n is also running in Docker, add it to the same network:

```powershell
# Create shared network
docker network create sap-network

# Run API in that network
docker run -d \
  --name sap-invoice-api \
  --network sap-network \
  -p 8000:8000 \
  --env-file .env \
  sap-invoice-api
```

Then in n8n, use:
- URL: `http://sap-invoice-api:8000/query` (internal network)
- or `http://localhost:8000/query` (from host)

## 📋 API Endpoints

Once running, test with:

```powershell
# Health check
curl http://localhost:8000/

# Query invoices
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d '{"question": "How many invoices in 2024?", "session_id": "test"}'

# Get count
curl http://localhost:8000/count

# Date range query
curl -X POST http://localhost:8000/invoices/date-range `
  -H "Content-Type: application/json" `
  -d '{"start_date": "2024-01-01", "end_date": "2024-12-31"}'
```

## 🔧 Environment Variables

Make sure `.env` file contains:
```
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pcsk_...
```

## 📊 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚀 Production Deployment

For production, consider:

1. **Use docker-compose.prod.yml** with:
   - Resource limits
   - Logging configuration
   - Volume mounts for persistent data
   
2. **Behind Nginx reverse proxy**:
   ```nginx
   location /api/ {
       proxy_pass http://sap-invoice-api:8000/;
   }
   ```

3. **Scale with Docker Swarm or Kubernetes**

## 🔍 Troubleshooting

```powershell
# Check if container is running
docker ps

# Check container logs
docker logs sap-invoice-api

# Restart container
docker restart sap-invoice-api

# Access container shell
docker exec -it sap-invoice-api /bin/bash
```
