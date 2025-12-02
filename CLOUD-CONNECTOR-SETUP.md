# SAP Cloud Connector - Quick Setup Guide

## Step 1: Download Cloud Connector

**Option A: Download via Browser**
1. Go to: https://tools.hana.ondemand.com/#cloud
2. Scroll to **"Cloud Connector"** section
3. Click **"Windows"** download link
4. Save `sapcc-2.17.1-windows-x64.zip` to `C:\Users\vthot\Downloads\`

**Option B: Direct Download Link**
Download directly: https://tools.hana.ondemand.com/additional/sapcc-2.17.1-windows-x64.zip

## Step 2: Install Cloud Connector

### Extract Files
```powershell
# Create installation directory
New-Item -Path "C:\SAP\CloudConnector" -ItemType Directory -Force

# Extract downloaded zip
Expand-Archive -Path "$env:USERPROFILE\Downloads\sapcc-2.17.1-windows-x64.zip" -DestinationPath "C:\SAP\CloudConnector" -Force
```

### Verify Installation
```powershell
cd C:\SAP\CloudConnector
dir
```

You should see files like:
- `go.bat` (startup script)
- `stop.bat` (shutdown script)
- `config_master` (configuration files)
- `tools` (utilities)

## Step 3: Start Cloud Connector

```powershell
cd C:\SAP\CloudConnector
.\go.bat
```

**Wait 30-60 seconds** for the service to start completely.

### Access Admin UI
Open browser to: https://localhost:8443

**Default Login:**
- Username: `Administrator`
- Password: `manage`

⚠️ **Important**: You'll be prompted to change the password on first login.

## Step 4: Configure BTP Subaccount Connection

### 4.1 Add Subaccount

1. In Cloud Connector UI, click **Connector** (left menu)
2. Click **Add Subaccount**
3. Enter these values:

```
Region: cf.us10.hana.ondemand.com
Subaccount: d57623dbtrial
Display Name: S4HANA Integration
Subaccount User: vthottempudi1@gmail.com
Password: [Your SAP BTP password]
Location ID: s4hana-connector
Description: Cloud Connector for S/4HANA OData access
```

4. Click **Save**

### 4.2 Verify Connection

- Status should change to **Connected** (green indicator)
- If fails, check:
  - BTP password is correct
  - Region matches your subaccount region
  - Internet connectivity

## Step 5: Configure S/4HANA System Access

### 5.1 Add System Mapping

1. Click **Cloud To On-Premise** (left menu)
2. In the **Mapping Virtual To Internal System** section, click **Add (+)**
3. Enter these values:

**System Details:**
```
Back-end Type: Non-SAP System
Protocol: HTTPS
Internal Host: s4hana2020.support.com
Internal Port: 8009
Virtual Host: s4hana-virtual.internal
Virtual Port: 8009
```

**Security Settings:**
```
Principal Type: None
Host in Request Header: Use Virtual Host
Description: S/4HANA 2020 OData Services
```

4. Click **Save**

### 5.2 Add Resource Paths

For the system you just created:

1. Click the **+** icon in the **Resources** column
2. Add these resources:

**Resource 1: All OData Services**
```
URL Path: /sap/opu/odata
Active: ✓ (checked)
Access Policy: Path And All Sub-Paths
Description: Allow all OData services
```

**Resource 2: Sales Service (Specific)**
```
URL Path: /sap/opu/odata/sap/ZSALE_SERVICE
Active: ✓ (checked)
Access Policy: Path And All Sub-Paths
Description: Sales Order OData Service
```

**Resource 3: Service Catalog**
```
URL Path: /sap/opu/odata/IWFND/CATALOGSERVICE
Active: ✓ (checked)
Access Policy: Path And All Sub-Paths
Description: OData Service Catalog
```

3. Click **Save** for each resource

### 5.3 Verify Configuration

Your configuration should look like:

```
┌──────────────────────────────────────────────────────┐
│ Virtual Host: s4hana-virtual.internal:8009           │
│ Internal Host: s4hana2020.support.com:8009           │
│                                                       │
│ Resources Accessible:                                │
│ ✓ /sap/opu/odata                                     │
│ ✓ /sap/opu/odata/sap/ZSALE_SERVICE                   │
│ ✓ /sap/opu/odata/IWFND/CATALOGSERVICE                │
└──────────────────────────────────────────────────────┘
```

## Step 6: Create BTP Destination

### 6.1 Access BTP Cockpit

1. Go to: https://cockpit.us10.hana.ondemand.com/
2. Login with: vthottempudi1@gmail.com
3. Navigate to: **Subaccounts** → **d57623dbtrial** → **Connectivity** → **Destinations**

### 6.2 Create New Destination

Click **New Destination** and enter:

**Basic Settings:**
```
Name: S4HANA_ODATA
Type: HTTP
Description: S/4HANA OData Services via Cloud Connector
URL: http://s4hana-virtual.internal:8009
Proxy Type: OnPremise
Authentication: BasicAuthentication
User: s4gui4
Password: Sap@123456
```

**Additional Properties** (click "New Property" for each):

| Property Name | Value |
|---------------|-------|
| `HTML5.DynamicDestination` | `true` |
| `WebIDEEnabled` | `true` |
| `WebIDEUsage` | `odata_abap` |
| `sap-client` | `100` |

If you set a Location ID in Step 4.1:
| Property Name | Value |
|---------------|-------|
| `CloudConnectorLocationId` | `s4hana-connector` |
| `CloudConnectorVersion` | `2` |

### 6.3 Test Destination

1. Click **Save**
2. Click **Check Connection**
3. Should see: ✓ **Connection to "S4HANA_ODATA" established**

## Step 7: Test End-to-End Connection

### 7.1 From Cloud Connector UI

1. Go to **Connector** → **Tunnel Info**
2. Verify:
   - **Tunnel Status**: Connected
   - **Tunnel State**: Available
   - **Last Request**: Should update when you test

### 7.2 Test via PowerShell

First get OAuth token:
```powershell
# Get XSUAA credentials
cf service-key n8n-xsuaa xsuaa-key
```

Copy the `clientid`, `clientsecret`, and `url` values, then:

```powershell
$clientId = "YOUR_CLIENT_ID"
$clientSecret = "YOUR_CLIENT_SECRET"
$tokenUrl = "YOUR_URL/oauth/token"

$body = @{
    grant_type = "client_credentials"
} | ConvertTo-Json

$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${clientId}:${clientSecret}"))

$response = Invoke-RestMethod -Uri $tokenUrl -Method Post -Headers @{
    Authorization = "Basic $auth"
    "Content-Type" = "application/x-www-form-urlencoded"
} -Body "grant_type=client_credentials"

$token = $response.access_token
echo "Access Token: $token"
```

Now test S/4HANA via Destination Service:

```powershell
$destUrl = "https://destination-configuration.cfapps.us10.hana.ondemand.com/destination-configuration/v1/destinations/S4HANA_ODATA/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view"

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri $destUrl -Method Get -Headers $headers
```

### 7.3 Expected Response

You should see sales order data like:
```xml
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <content type="application/xml">
      <properties>
        <SalesOrder>1</SalesOrder>
        <SalesOrderType>OR</SalesOrderType>
        ...
      </properties>
    </content>
  </entry>
</feed>
```

## Step 8: Import n8n Workflow

Now that Cloud Connector is configured, import the workflow:

1. Go to: https://vthottempudi1.app.n8n.cloud
2. **Workflows** → **Add Workflow** → **Import from File**
3. Select: `n8n-btp-destination-workflow.json`
4. Update the **"Set XSUAA Credentials"** node with values from Step 7.2
5. Execute the workflow

## Troubleshooting

### Cloud Connector Won't Start

**Problem**: `go.bat` doesn't start the service

**Solutions**:
```powershell
# Check Java version (Cloud Connector needs Java 8 or 11)
java -version

# If Java not installed, download from:
# https://www.oracle.com/java/technologies/downloads/#java11-windows

# Restart Cloud Connector
cd C:\SAP\CloudConnector
.\stop.bat
.\go.bat
```

### Connection to BTP Failed

**Problem**: Subaccount shows "Not Connected"

**Check**:
1. Credentials are correct
2. Region is correct (`cf.us10.hana.ondemand.com` for US10)
3. Subaccount ID is correct (`d57623dbtrial`)

**Get correct values**:
```powershell
cf target
# Shows: org, space, and API endpoint

# Extract region from API endpoint
# api.cf.us10.hana.ondemand.com → cf.us10.hana.ondemand.com
```

### S/4HANA System Not Accessible

**Problem**: Resources show as unreachable

**Check**:
1. Can you ping from Cloud Connector host?
   ```powershell
   ping s4hana2020.support.com
   ```
2. Is port 8009 accessible?
   ```powershell
   Test-NetConnection -ComputerName s4hana2020.support.com -Port 8009
   ```
3. Is the hostname in Windows hosts file?
   ```
   C:\Windows\System32\drivers\etc\hosts
   49.206.196.74 s4hana2020.support.com
   ```

### Destination Check Connection Fails

**Problem**: "Connection to 'S4HANA_ODATA' failed"

**Solutions**:
1. Verify Cloud Connector is running and connected
2. Check Virtual Host matches exactly: `s4hana-virtual.internal`
3. Verify Location ID matches (if set)
4. Check authentication credentials: `s4gui4` / `Sap@123456`

## Managing Cloud Connector

### Start Cloud Connector
```powershell
cd C:\SAP\CloudConnector
.\go.bat
```

### Stop Cloud Connector
```powershell
cd C:\SAP\CloudConnector
.\stop.bat
```

### View Logs
```powershell
cd C:\SAP\CloudConnector
notepad .\log\ljs_trace.log
```

### Check Status
Open browser: https://localhost:8443

## Security Best Practices

1. **Change default password** immediately after first login
2. **Restrict resource paths** to only what's needed
3. **Use Location ID** to isolate different environments
4. **Monitor audit logs** regularly
5. **Keep Cloud Connector updated** with latest patches
6. **Use strong authentication** for S/4HANA (consider certificates)

## Next Steps

✅ Cloud Connector installed and running
✅ Connected to BTP subaccount
✅ S/4HANA system mapped
✅ Resources configured
✅ BTP Destination created
✅ Connection tested

Now you can:
1. Import `n8n-btp-destination-workflow.json` into n8n Cloud
2. Configure XSUAA credentials in the workflow
3. Execute the workflow to sync S/4HANA data to PostgreSQL
4. Set up scheduled sync (hourly/daily)

## Architecture Overview

```
┌─────────────────┐
│   n8n Cloud     │
│  (External)     │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   SAP BTP       │
│ Destination Svc │
└────────┬────────┘
         │ Secure Tunnel
         ▼
┌─────────────────┐
│ Cloud Connector │ ← Running on your machine
│  (On-Premise)   │    (C:\SAP\CloudConnector)
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   S/4HANA 2020  │
│ s4hana2020...   │
│    Port 8009    │
└─────────────────┘
```

The Cloud Connector creates an **outbound** connection to BTP, so you don't need to open any inbound firewall ports!
