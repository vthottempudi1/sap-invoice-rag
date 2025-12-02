# n8n Workflow: S/4HANA via BTP Destination Service Setup Guide

## Prerequisites

Before using this workflow, you need to configure SAP BTP services and Cloud Connector.

## Step 1: Get XSUAA Service Credentials

1. **Create XSUAA service key** (if not already created):
   ```powershell
   cf create-service-key n8n-xsuaa xsuaa-key
   ```

2. **Get the credentials**:
   ```powershell
   cf service-key n8n-xsuaa xsuaa-key
   ```

3. **Copy these values** from the output:
   - `clientid` 
   - `clientsecret`
   - `url` (authentication endpoint, e.g., `https://your-subdomain.authentication.us10.hana.ondemand.com`)

4. **Update the "Set XSUAA Credentials" node** in the workflow with your values:
   ```javascript
   const xsuaaCredentials = {
     clientId: 'sb-xxxxx-your-client-id',
     clientSecret: 'your-secret-here',
     tokenEndpoint: 'https://your-subdomain.authentication.us10.hana.ondemand.com/oauth/token',
     url: 'https://your-subdomain.authentication.us10.hana.ondemand.com'
   };
   ```

## Step 2: Install SAP Cloud Connector

### Download and Install

1. Go to https://tools.hana.ondemand.com/#cloud
2. Download **SAP Cloud Connector** for Windows
3. Install or extract to `C:\SAP\CloudConnector`

### Start Cloud Connector

```powershell
cd C:\SAP\CloudConnector
.\go.bat
```

Access UI at: https://localhost:8443
- Username: `Administrator`
- Password: `manage` (change on first login)

## Step 3: Connect Cloud Connector to BTP

1. In Cloud Connector UI, go to **Connector** → **Define Subaccount**

2. Enter your BTP details:
   ```
   Region Host: cf.us10.hana.ondemand.com
   Subaccount: d57623dbtrial
   Display Name: S4HANA Connector
   Subaccount User: vthottempudi1@gmail.com
   Password: [Your BTP password]
   Location ID: s4hana-prod (optional)
   Description: Connection to on-premise S/4HANA
   ```

3. Click **Save**

4. Wait for status to show **Connected** (green)

## Step 4: Configure S/4HANA System Access

1. In Cloud Connector, go to **Cloud To On-Premise** → **Access Control**

2. Click **Add** (+ icon) to add a system mapping:

   ```
   Back-end Type: Non-SAP System
   Protocol: HTTPS
   Internal Host: s4hana2020.support.com
   Internal Port: 8009
   Virtual Host: s4hana-odata.internal
   Virtual Port: 8009
   Principal Type: None
   Host in Request Header: Use Virtual Host
   Description: S/4HANA OData Services
   ```

3. Click **Save**

4. Click **Add** (+ icon) in the **Resources** section to allow specific paths:

   **Resource 1: OData Services**
   ```
   URL Path: /sap/opu/odata
   Active: ✓
   Access Policy: Path And All Sub-Paths
   Description: Allow all OData services
   ```

   **Resource 2: Specific Sales Service**
   ```
   URL Path: /sap/opu/odata/sap/ZSALE_SERVICE
   Active: ✓
   Access Policy: Path And All Sub-Paths
   Description: Sales Order OData Service
   ```

5. Click **Save**

## Step 5: Create BTP Destination

1. Go to **SAP BTP Cockpit** → Your Subaccount → **Connectivity** → **Destinations**

2. Click **New Destination**

3. Enter these **exact** values:

   ```
   Name: S4HANA_ODATA
   Type: HTTP
   Description: S/4HANA OData via Cloud Connector
   URL: http://s4hana-odata.internal:8009
   Proxy Type: OnPremise
   Authentication: BasicAuthentication
   User: s4gui4
   Password: Sap@123456
   ```

4. Click **New Property** and add:

   | Property | Value |
   |----------|-------|
   | `CloudConnectorLocationId` | `s4hana-prod` (if you set one) |
   | `CloudConnectorVersion` | `2` |
   | `WebIDEEnabled` | `true` |
   | `WebIDEUsage` | `odata_abap` |

5. Click **Save**

6. Click **Check Connection** to verify

## Step 6: Create PostgreSQL Table

Before running the workflow, create the database table:

```sql
CREATE TABLE IF NOT EXISTS sales_orders (
    sales_order VARCHAR(10) PRIMARY KEY,
    sales_order_type VARCHAR(4),
    created_by_user VARCHAR(12),
    sales_organization VARCHAR(4),
    sold_to_party VARCHAR(10),
    sales_order_date TIMESTAMP,
    total_net_amount DECIMAL(15,2),
    transaction_currency VARCHAR(5),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales_orders(sales_order_date);
CREATE INDEX IF NOT EXISTS idx_customer ON sales_orders(sold_to_party);
```

## Step 7: Import Workflow into n8n Cloud

1. Go to https://vthottempudi1.app.n8n.cloud
2. Click **Workflows** → **Add Workflow**
3. Click **⋮** menu → **Import from File**
4. Select `n8n-btp-destination-workflow.json`

## Step 8: Configure Workflow Nodes

### Node 1: Set XSUAA Credentials

Update with your actual XSUAA service key values:

```javascript
const xsuaaCredentials = {
  clientId: 'sb-your-actual-client-id',
  clientSecret: 'your-actual-secret',
  tokenEndpoint: 'https://your-subdomain.authentication.us10.hana.ondemand.com/oauth/token',
  url: 'https://your-subdomain.authentication.us10.hana.ondemand.com'
};
```

### Node 2: Prepare Destination Call

Update destination name if different:

```javascript
destinationName: 'S4HANA_ODATA',  // Must match BTP Destination name
```

### Node 3: Store in PostgreSQL

Link to your PostgreSQL credential:
- Host: `postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com`
- Port: `6974`
- Database: `XMCMDsOblizg`
- User: `7842af8b9020`
- Password: `c7b61e26789d9b8a32e285396b749a29`

## Step 9: Test the Workflow

1. **Start Cloud Connector** (must be running!)
   ```powershell
   cd C:\SAP\CloudConnector
   .\go.bat
   ```

2. **Verify Connection**:
   - Cloud Connector UI → Check status is **Connected**
   - BTP Cockpit → Destinations → **S4HANA_ODATA** → Check Connection ✓

3. **Execute n8n Workflow**:
   - Open workflow in n8n Cloud
   - Click **Execute Workflow**
   - Monitor each node's output

## Workflow Flow

```
┌─────────────────┐
│ Manual Trigger  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Set XSUAA Credentials   │ ← Update with your values
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Get OAuth Token         │ → POST to XSUAA /oauth/token
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Prepare Destination     │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Call S/4HANA via Destination Service │
│                                      │
│ BTP Destination Service              │
│         ↓                            │
│ SAP Cloud Connector                  │
│         ↓                            │
│ S/4HANA (s4hana2020.support.com)    │
└────────┬─────────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Parse Sales Orders      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Store in PostgreSQL     │
└─────────────────────────┘
```

## Troubleshooting

### Error: "Connection to Cloud Connector failed"

**Check:**
1. Is Cloud Connector running? (`https://localhost:8443`)
2. Is status **Connected** in Cloud Connector UI?
3. Is the Location ID correct in Destination properties?

**Fix:**
```powershell
# Restart Cloud Connector
cd C:\SAP\CloudConnector
.\stop.bat
.\go.bat
```

### Error: "401 Unauthorized" from XSUAA

**Check:**
1. Are `clientId` and `clientSecret` correct?
2. Is the token endpoint URL correct?

**Fix:**
```powershell
# Get fresh credentials
cf service-key n8n-xsuaa xsuaa-key
```

### Error: "Destination not found"

**Check:**
1. Destination name matches exactly: `S4HANA_ODATA`
2. Destination exists in BTP Cockpit → Connectivity → Destinations

**Fix:**
- Recreate destination following Step 5

### Error: "Host not found: s4hana-odata.internal"

**Check:**
1. Is the Virtual Host in Cloud Connector exactly `s4hana-odata.internal`?
2. Is the Destination URL exactly `http://s4hana-odata.internal:8009`?

**Fix:**
- Update Cloud Connector virtual host OR
- Update Destination URL to match

### Error: "404 Not Found" from S/4HANA

**Check:**
1. Are the Resources configured in Cloud Connector?
2. Is `/sap/opu/odata` path allowed?

**Fix:**
- Add resource in Cloud Connector: `/sap/opu/odata` with "Path And All Sub-Paths"

## Testing Individual Components

### Test 1: XSUAA Authentication

```powershell
# Test OAuth token retrieval
$clientId = "your-client-id"
$clientSecret = "your-client-secret"
$tokenUrl = "https://your-subdomain.authentication.us10.hana.ondemand.com/oauth/token"

$body = @{
    grant_type = "client_credentials"
    client_id = $clientId
    client_secret = $clientSecret
}

Invoke-RestMethod -Uri $tokenUrl -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
```

### Test 2: Cloud Connector Connectivity

In Cloud Connector UI:
1. Go to **Connector** → **Tunnel Info**
2. Check **Tunnel Status** = **Connected**
3. Note the **Location ID**

### Test 3: Destination Service

```powershell
# Replace with your actual access token
$token = "your-access-token-from-xsuaa"
$destUrl = "https://destination-configuration.cfapps.us10.hana.ondemand.com/destination-configuration/v1/destinations/S4HANA_ODATA"

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri $destUrl -Method Get -Headers $headers
```

### Test 4: End-to-End S/4HANA Call

Using the Destination Service to proxy to S/4HANA:

```powershell
$token = "your-access-token"
$url = "https://destination-configuration.cfapps.us10.hana.ondemand.com/destination-configuration/v1/destinations/S4HANA_ODATA/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view"

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri $url -Method Get -Headers $headers
```

## Schedule Automatic Sync

To run this workflow automatically:

1. Replace **Manual Trigger** with **Schedule Trigger**
2. Configure schedule:
   - **Mode**: Interval
   - **Interval**: Every 1 hour (or as needed)
   - **Start Time**: Now

## Security Best Practices

1. **Never commit credentials** to version control
2. Use **n8n environment variables** for sensitive data
3. **Rotate XSUAA secrets** periodically
4. **Monitor Cloud Connector** logs for unauthorized access
5. **Restrict Cloud Connector resources** to minimum required paths

## Benefits of This Approach

✅ **Secure**: Cloud Connector establishes outbound connection only (no firewall changes)
✅ **Centralized**: BTP Destination Service manages all connection configurations
✅ **Auditable**: All requests logged in BTP and Cloud Connector
✅ **Scalable**: Multiple services can use same Cloud Connector tunnel
✅ **Flexible**: Easy to switch between DEV/QA/PROD systems by changing destinations

## Alternative: Direct Connection (No Cloud Connector)

If your S/4HANA system is already publicly accessible (which it appears to be since you can access it from your local machine), you can use the simpler direct connection workflow instead:

Use `n8n-s4hana-sales-to-postgres.json` which directly calls:
- URL: `https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view`
- Auth: Basic Auth (s4gui4/Sap@123456)
- SSL: Allow unauthorized certificates

Cloud Connector is only needed when S/4HANA is **NOT** accessible from the internet.
