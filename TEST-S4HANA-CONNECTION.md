# Test S/4HANA Connection in n8n Cloud

## Quick Setup (5 Minutes)

### Step 1: Create S/4HANA Credential in n8n Cloud

1. **Go to n8n Cloud**: https://vthottempudi1.app.n8n.cloud

2. **Click your profile icon** (top-right) → **Credentials**

3. **Click "+ Add Credential"**

4. **Search for**: `HTTP Basic Auth`

5. **Fill in**:
   ```
   Credential Name: S/4HANA Basic Auth
   Username: s4gui4
   Password: Sap@123456
   ```

6. **Click "Save"**

---

### Step 2: Import Test Workflow

1. **In n8n Cloud**, click **Workflows** (left sidebar)

2. **Click "+ Add Workflow"**

3. **Click the "⋮" menu** (top-right) → **Import from File**

4. **Select**: `n8n-s4hana-test-connection.json`

5. **Click "Import"**

---

### Step 3: Configure the Workflow

The workflow has **3 simple nodes**:

#### Node 1: Manual Trigger
- No configuration needed
- Click this to run the test

#### Node 2: Fetch Sales Orders from S/4HANA
- **Type**: HTTP Request
- **Authentication**: Select your "S/4HANA Basic Auth" credential
- **URL**: `https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view`
- **Method**: GET
- **Headers**: Accept: application/json
- **Options**: 
  - ✅ Allow Unauthorized Certificates (checked)
  - Timeout: 30000

#### Node 3: Display Results
- **Type**: Code
- Shows formatted output with connection status and sales orders
- No configuration needed

---

### Step 4: Test the Connection

1. **Click "Execute Workflow"** button (top-right, play icon ▶)

2. **Watch the execution**:
   - Node 1 ✓ Triggers
   - Node 2 → Fetches data from S/4HANA
   - Node 3 → Displays formatted results

3. **Check the output** in Node 3:
   ```json
   {
     "status": "SUCCESS",
     "message": "Successfully connected to S/4HANA!",
     "timestamp": "2025-11-21T...",
     "total_orders": 14,
     "sales_orders": [
       {
         "SalesOrder": "1",
         "SalesOrderType": "OR",
         "Customer": "17100001",
         "SalesOrg": "1710",
         "OrderDate": "2021-01-15",
         "Amount": "52000.00",
         "Currency": "USD"
       },
       ...
     ]
   }
   ```

---

## Expected Results

✅ **SUCCESS** - You should see:
- Status: "SUCCESS"
- Message: "Successfully connected to S/4HANA!"
- total_orders: 14
- List of sales orders with details

---

## Troubleshooting

### Issue 1: "Could not resolve host: s4hana2020.support.com"

**Problem**: n8n Cloud cannot resolve the hostname

**Solution**: Try using the IP address instead:

In the HTTP Request node, change the URL to:
```
https://49.206.196.74:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view
```

And add this header:
```
Name: Host
Value: s4hana2020.support.com
```

---

### Issue 2: "SSL certificate problem"

**Problem**: Self-signed certificate not trusted

**Solution**: Ensure "Allow Unauthorized Certificates" is ✅ **checked** in the HTTP Request node options

---

### Issue 3: "401 Unauthorized"

**Problem**: Authentication failed

**Solution**: 
1. Verify credential in n8n Cloud:
   - Username: `s4gui4`
   - Password: `Sap@123456`
2. Make sure the credential is selected in the HTTP Request node

---

### Issue 4: "Connection timeout"

**Problem**: S/4HANA server not reachable from n8n Cloud

**Solution**: Your S/4HANA might not be accessible from n8n Cloud's servers. Test from your local machine:

```powershell
curl.exe -k -u s4gui4:Sap@123456 https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view
```

If this works but n8n Cloud fails, your S/4HANA is **not publicly accessible** and you'll need Cloud Connector.

---

## Alternative: Test with IP Address

If hostname fails, try this workflow variation:

1. **Edit Node 2** (HTTP Request)
2. **Change URL to**:
   ```
   https://49.206.196.74:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view
   ```
3. **Add Header**:
   - Name: `Host`
   - Value: `s4hana2020.support.com`
4. **Execute again**

---

## What This Test Proves

✅ **If successful**: 
- S/4HANA is accessible from n8n Cloud
- Authentication is working
- OData service is responding
- You can proceed with full integration

❌ **If it fails with timeout**:
- S/4HANA is not publicly accessible
- You need Cloud Connector setup
- Or use local n8n Docker instead

---

## Next Steps After Success

Once the test works:

1. **Add data transformation** (already have the workflow ready)
2. **Add schedule trigger** for automatic sync
3. **Add error handling** and notifications
4. **Monitor executions** in n8n Cloud dashboard

---

## Simple Workflow Diagram

```
┌──────────────────┐
│ Manual Trigger   │ ← Click to test
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ HTTP Request to S/4HANA             │
│ https://s4hana2020.support.com:8009 │
│ Auth: s4gui4 / Sap@123456           │
│ SSL: Allow Self-Signed Cert         │
└────────┬────────────────────────────┘
         │
         │ JSON Response (OData)
         │
         ▼
┌──────────────────────────────────┐
│ Display Results                  │
│ - Connection Status              │
│ - Number of Orders               │
│ - Sales Order Details            │
└──────────────────────────────────┘
```

---

## Test Checklist

- [ ] S/4HANA Basic Auth credential created in n8n Cloud
- [ ] Test workflow imported (`n8n-s4hana-test-connection.json`)
- [ ] HTTP Request node has credential selected
- [ ] "Allow Unauthorized Certificates" is checked
- [ ] Workflow executed successfully
- [ ] Output shows 14 sales orders
- [ ] Connection confirmed working!

---

## Need Help?

**Verify S/4HANA from your machine**:
```powershell
curl.exe -k -u s4gui4:Sap@123456 https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view
```

**Check n8n Cloud executions**:
- Go to **Executions** in left sidebar
- Click on the latest execution
- Check each node's input/output
- Look for error messages

**Your n8n Cloud**: https://vthottempudi1.app.n8n.cloud/workflows
