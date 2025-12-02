# Test All S/4HANA OData Services

## Quick Test Guide (5 minutes)

### When to Use This
Run this test **after your S/4HANA server is back online** to verify which OData services are available.

---

## Step 1: Import Test Workflow

1. Open n8n Cloud: `https://vthottempudi1.app.n8n.cloud`
2. Go to **Workflows** → **Add Workflow** → **Import from File**
3. Select: `test-s4hana-services.json`
4. Click **Import**

---

## Step 2: Run the Test

1. Make sure your **S/4HANA server is online** (test with ping or curl first)
2. Click **"Test workflow"** button
3. Wait ~10 seconds for all 4 services to be tested
4. Check the **Summary Report** node output

---

## Step 3: Read the Results

The Summary Report will show:

```json
{
  "summary": "2/4 services are working",
  "server": "49.206.196.74:8009",
  "results": [
    {
      "service": "Sales Orders (ZSALE_SERVICE)",
      "url": "/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view",
      "status": "✅ SUCCESS",
      "recordCount": 3,
      "error": null
    },
    {
      "service": "Purchase Orders (ZPURCHASE_SERVICE)",
      "url": "/sap/opu/odata/sap/ZPURCHASE_SERVICE/zpurchase_view",
      "status": "❌ FAILED",
      "recordCount": 0,
      "error": "404 Not Found"
    }
    // ... etc
  ]
}
```

---

## Step 4: Update AI Agent Workflow

Based on the test results:

### ✅ If a service is **SUCCESS**
- Keep the tool in your AI agent workflow
- It's ready to use!

### ❌ If a service is **FAILED**
- **404 Not Found**: Service doesn't exist on your S/4HANA system
  - Ask your SAP admin for the correct service name
  - Or remove this tool from the AI agent
  
- **401 Unauthorized**: Authentication issue
  - Check credentials in n8n
  
- **500 Internal Server Error**: Service exists but has errors
  - Check SAP Gateway logs
  - May need activation in `/IWFND/MAINT_SERVICE`

---

## Alternative: Manual Testing with PowerShell

If you prefer command-line testing:

```powershell
# Test Sales Orders (known working)
curl.exe -k -u s4gui4:Sap@123456 "https://49.206.196.74:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view?`$format=json&`$top=3" -H "Accept: application/json" -H "Host: s4hana2020.support.com"

# Test Purchase Orders
curl.exe -k -u s4gui4:Sap@123456 "https://49.206.196.74:8009/sap/opu/odata/sap/ZPURCHASE_SERVICE/zpurchase_view?`$format=json&`$top=3" -H "Accept: application/json" -H "Host: s4hana2020.support.com"

# Test Inventory
curl.exe -k -u s4gui4:Sap@123456 "https://49.206.196.74:8009/sap/opu/odata/sap/ZINVENTORY_SERVICE/zinventory_view?`$format=json&`$top=3" -H "Accept: application/json" -H "Host: s4hana2020.support.com"

# Test Customer Master
curl.exe -k -u s4gui4:Sap@123456 "https://49.206.196.74:8009/sap/opu/odata/sap/ZCUSTOMER_SERVICE/zcustomer_view?`$format=json&`$top=3" -H "Accept: application/json" -H "Host: s4hana2020.support.com"
```

**Good Response (200 OK):**
```json
{
  "d": {
    "results": [
      { "SalesOrder": "1", "Customer": "25100080", ... }
    ]
  }
}
```

**Bad Response (404 Not Found):**
```xml
<error xmlns="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <code>/IWFND/CM_MGW_RT/022</code>
  <message xml:lang="en">Resource not found for segment 'zpurchase_view'</message>
</error>
```

---

## Step 5: Get Correct Service Names

If services fail, check in SAP:

### Option A: Gateway Service Builder
1. Log into SAP GUI
2. Transaction: `/IWFND/MAINT_SERVICE`
3. Search for services starting with `Z`
4. Note the **Service Name** and **Entity Set** names

### Option B: Service Catalog
1. Transaction: `/IWFND/GW_CLIENT`
2. Browse available services
3. Test services directly in SAP

### Option C: Ask SAP Admin
- Which OData services are exposed for:
  - Sales Orders
  - Purchase Orders  
  - Inventory/Stock
  - Customer Master
  - Material Master

---

## Common S/4HANA OData Service Names

If your custom services don't exist, try these standard SAP services:

| Data Type | Standard Service Name | Entity Set |
|-----------|----------------------|------------|
| Sales Orders | `API_SALES_ORDER_SRV` | `A_SalesOrder` |
| Purchase Orders | `API_PURCHASEORDER_PROCESS_SRV` | `A_PurchaseOrder` |
| Material Stock | `API_MATERIAL_STOCK_SRV` | `A_MatlStkInAcctMod` |
| Customer Master | `API_BUSINESS_PARTNER` | `A_Customer` |
| Material Master | `API_MATERIAL_SRV` | `A_Material` |

Example URL for standard service:
```
https://49.206.196.74:8009/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder?$format=json&$top=3
```

---

## Next Steps

Once you know which services work:

1. **Update AI agent workflow** - Remove tools for non-working services
2. **Test AI agent** - Ask questions using working data sources
3. **Add filters** - Enhance tools with OData filters if needed
4. **Schedule sync** - Set up regular data fetches to Google Sheets

---

## Troubleshooting

**Server unreachable:**
- Check if S/4HANA is running
- Verify VPN connection (if required)
- Test: `Test-NetConnection -ComputerName 49.206.196.74 -Port 8009`

**All services fail with 404:**
- Service names might be different
- Check `/IWFND/MAINT_SERVICE` in SAP
- Services may need activation

**Timeout errors:**
- Increase timeout in n8n (currently 30000ms = 30 seconds)
- Check network latency
- SAP system may be slow

---

## Questions?

- Which services showed ✅ SUCCESS?
- What errors did you see for ❌ FAILED services?
- Do you need help finding the correct service names in SAP?
