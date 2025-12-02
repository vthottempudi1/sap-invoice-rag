# n8n SAP BTP Integration Guide

## Overview
This guide explains how to connect n8n (running locally in Docker) to SAP PostgreSQL on Cloud Foundry and read OData services.

## Current Setup

### Services on Cloud Foundry
- **PostgreSQL**: `n8n-database` (trial plan on AWS RDS)
  - Host: `postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com`
  - Port: `6974`
  - Database: `XMCMDsOblizg`
  - Username: `30b40be4db3f`
  - Password: `e694313dfb09a85a0f5`

- **XSUAA**: `n8n-xsuaa` (authentication service)
- **Destination**: `n8n-destination` (lite plan)

### Docker Containers
- **n8n**: Running on `http://localhost:5678`
  - Credentials: `admin` / `your-secure-password`
  - Network: Docker bridge (172.17.0.x)
  
- **OData Service**: Running on `http://172.17.0.3:3000`
  - Endpoint: `/odata/v4/Products`
  - Sample data: 5 products (Laptop, Mouse, Keyboard, Monitor, Desk)

## Step-by-Step Setup

### 1. Access n8n
Open browser: `http://localhost:5678`
Login with credentials above.

### 2. Create PostgreSQL Credential in n8n
1. Go to **Credentials** → **Add Credential**
2. Search for "Postgres"
3. Fill in:
   - **Name**: SAP PostgreSQL
   - **Host**: `postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com`
   - **Port**: `6974`
   - **Database**: `XMCMDsOblizg`
   - **User**: `30b40be4db3f`
   - **Password**: `e694313dfb09a85a0f5`
   - **SSL**: Enabled (required for AWS RDS)
4. Click **Create**

### 3. Create Products Table in PostgreSQL
Since CF routes quota is exceeded, run this SQL directly from n8n:

1. Create a new workflow
2. Add **Postgres** node
3. Select credential "SAP PostgreSQL"
4. Operation: **Execute Query**
5. Query:
```sql
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2),
    stock INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);
```
6. Execute manually once

### 4. Import OData to PostgreSQL Workflow
1. In n8n, go to **Workflows** → **Import from File**
2. Select `n8n-odata-to-postgres-workflow.json`
3. Configure credentials:
   - **SAP PostgreSQL**: Select the credential created in step 2
   - **SAP BTP OAuth2**: Create if needed with:
     - Client ID: `sb-clone5e3f101cee3a4c37ac9411cb9b267198!b554331|destination-xsappname!b62`
     - Client Secret: `3e86eca2-e9e0-4c2d-998c-58dd1f0c8cb0$UqgqYN5oRSoMANZT79wNt2RpfKw9X3lx6-5KWpGLx4g=`
     - Access Token URL: `https://d57623dbtrial.authentication.us10.hana.ondemand.com/oauth/token`
     - Scope: Leave empty
     - Authentication: Basic Auth Header

### 5. Test the Workflow
1. Click **Execute Workflow** button
2. Verify each node shows success (green checkmark)
3. Check data flow:
   - Schedule Trigger → triggers hourly
   - Get OAuth Token → retrieves Bearer token
   - Read OData Products → fetches from `http://172.17.0.3:3000`
   - Store in PostgreSQL → upserts into SAP database

### 6. Verify Data in PostgreSQL
Create another workflow to query:
1. Add **Postgres** node with "SAP PostgreSQL" credential
2. Operation: **Execute Query**
3. Query: `SELECT * FROM products ORDER BY created_at DESC`
4. Execute and view results

## Troubleshooting

### Issue: PostgreSQL Connection Refused
**Cause**: SAP PostgreSQL on Cloud Foundry is in a private network, not directly accessible from local Docker.

**Solution**: The connection should work because:
- SAP PostgreSQL is on AWS RDS with public endpoint
- SSL is enabled for secure connections
- Credentials include proper hostname and port

If connection fails, verify:
```powershell
# Test DNS resolution
nslookup postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com

# Test port connectivity (may timeout due to security groups)
Test-NetConnection -ComputerName postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com -Port 6974
```

### Issue: OData Service Unreachable
**Solution**: Ensure OData container is running:
```powershell
docker ps | Select-String "odata"
```

If not running, start it:
```powershell
cd odata-service
docker build -t odata-service .
docker run -d --name odata-service -p 3000:3000 --network bridge odata-service
```

### Issue: Routes Quota Exceeded
**Cause**: SAP trial account has 0 routes quota, preventing CF app deployments.

**Workaround**: Use local n8n Docker instance instead of n8n Cloud. PostgreSQL on CF is accessible via public endpoint with SSL.

## Architecture

```
┌─────────────────────┐
│  n8n Docker         │
│  localhost:5678     │
└──────────┬──────────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
┌──────────────────┐  ┌────────────────────────┐
│  OData Service   │  │  SAP PostgreSQL (CF)   │
│  172.17.0.3:3000│  │  AWS RDS us-east-1     │
│  Docker Network  │  │  Port 6974 (SSL)       │
└──────────────────┘  └────────────────────────┘
```

## Workflow Logic

1. **Schedule Trigger**: Runs hourly (configurable)
2. **Get OAuth Token**: Authenticates with SAP BTP XSUAA
3. **Read OData Products**: Fetches product data from OData V4 service
4. **Store in PostgreSQL**: Upserts each product into SAP database
   - Uses `ON CONFLICT` to update existing records
   - Tracks `created_at` and `updated_at` timestamps

## Next Steps

1. **Add Error Handling**: 
   - Add "Error Trigger" nodes
   - Send notifications on failure

2. **Data Transformation**:
   - Add "Set" or "Code" nodes to transform data
   - Apply business logic before storing

3. **Advanced Queries**:
   - Add OData `$filter`, `$select`, `$top` parameters
   - Implement incremental data sync

4. **Monitoring**:
   - Check execution history in n8n
   - Set up alerts for failed executions

## Resources

- n8n Documentation: https://docs.n8n.io
- SAP BTP Documentation: https://help.sap.com/docs/btp
- OData V4 Specification: https://www.odata.org/documentation/
