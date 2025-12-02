# S/4HANA to Google Sheets Integration Guide

## Overview
Sync S/4HANA sales orders directly to Google Sheets for easy analysis and sharing - no database setup required!

**What you'll have:**
- Automatic sync of sales orders from S/4HANA to Google Sheets
- Historical data tracking with timestamps
- Easy filtering, sorting, and pivot tables in Google Sheets
- Share with your team without n8n access

---

## Part 1: Create Google Sheet

### Step 1.1: Create New Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Click **+ Blank** to create new spreadsheet
3. Name it: **S/4HANA Sales Orders**

### Step 1.2: Add Column Headers

In Row 1, add these headers (copy-paste this row):

```
SalesOrder	SalesOrderType	SalesOrderDate	CreatedByUser	SalesOrganization	DistributionChannel	Customer	CustomerGroup	PurchaseOrder	TotalAmount	Currency	RequestedDeliveryDate	ShippingCondition	PaymentTerms	BillingBlock	OverallStatus	FetchedAt
```

**Or manually type:**
- A1: `SalesOrder`
- B1: `SalesOrderType`
- C1: `SalesOrderDate`
- D1: `CreatedByUser`
- E1: `SalesOrganization`
- F1: `DistributionChannel`
- G1: `Customer`
- H1: `CustomerGroup`
- I1: `PurchaseOrder`
- J1: `TotalAmount`
- K1: `Currency`
- L1: `RequestedDeliveryDate`
- M1: `ShippingCondition`
- N1: `PaymentTerms`
- O1: `BillingBlock`
- P1: `OverallStatus`
- Q1: `FetchedAt`

### Step 1.3: Format the Sheet (Optional)

1. **Bold the headers**: Select row 1 → Click **B** (Bold)
2. **Freeze header row**: View → Freeze → 1 row
3. **Format Amount column**: Select column J → Format → Number → Currency
4. **Auto-resize columns**: Select all → Right-click column header → Resize columns → Fit to data

---

## Part 2: Setup n8n Cloud Integration

### Step 2.1: Connect Google Sheets to n8n

1. **Go to n8n Cloud**: https://vthottempudi1.app.n8n.cloud

2. **Add Google Sheets Credential**:
   - Click profile icon → **Credentials**
   - Click **+ Add Credential**
   - Search for: **Google Sheets OAuth2 API**
   - Click **Sign in with Google**
   - Select your Google account
   - Click **Allow** to grant permissions
   - Click **Save**

### Step 2.2: Import Workflow

1. **In n8n Cloud**, click **Workflows** → **+ Add Workflow**
2. Click **⋮ menu** → **Import from File**
3. Select: `n8n-s4hana-to-google-sheets.json`
4. Click **Import**

---

## Part 3: Configure the Workflow

The workflow has **5 nodes**:

### Node 1: Manual Trigger
- No configuration needed
- Click to run the sync manually

### Node 2: Fetch Sales Orders from S/4HANA
- **Credential**: Select your **S/4HANA Basic Auth** (s4gui4/Sap@123456)
- Already configured to use IP address: `49.206.196.74:8009`
- Fetches up to 100 sales orders

### Node 3: Transform for Google Sheets
- Converts SAP OData format to Google Sheets rows
- Parses SAP date format (/Date(timestamp)/)
- No configuration needed

### Node 4: Append to Google Sheets
- **Credential**: Select your **Google Sheets OAuth2 API**
- **Document**: Click dropdown → Select **S/4HANA Sales Orders**
- **Sheet**: Select **Sheet1**
- **Mapping Mode**: Auto-map input data
- **Matching Column**: `SalesOrder` (to prevent duplicates)
- Click **Save**

### Node 5: Sync Summary
- Shows how many orders were synced
- No configuration needed

---

## Part 4: Test the Integration

### Step 4.1: First Run

1. **Execute Workflow**: Click **Execute Workflow** button ▶
2. **Wait for completion** (5-10 seconds)
3. **Check Node 5 output**:
   ```json
   {
     "status": "SUCCESS",
     "message": "Synced 15 sales orders to Google Sheets",
     "timestamp": "2025-11-21T..."
   }
   ```

### Step 4.2: Verify in Google Sheets

1. **Open your Google Sheet**: S/4HANA Sales Orders
2. **You should see**:
   - Row 1: Headers
   - Row 2+: Sales order data
   - Sales Order 1, 2, 3, 4, 5, etc.

### Step 4.3: Check Data Quality

Verify a few records:
- **SalesOrder**: Should have numbers like 1, 2, 3, etc.
- **TotalAmount**: Should show currency amounts (400.00, 10.00, etc.)
- **SalesOrderDate**: Should be formatted as YYYY-MM-DD
- **FetchedAt**: Should show current timestamp

---

## Part 5: Schedule Automatic Sync

### Option A: Hourly Sync

1. **In workflow editor**, click **+** to add node
2. Search for: **Schedule Trigger**
3. Configure:
   ```
   Trigger Interval: Hours
   Hours Between Triggers: 1
   ```
4. **Connect** Schedule Trigger → Fetch Sales Orders node
5. **Remove** Manual Trigger (or keep for on-demand syncs)
6. **Activate workflow**: Toggle **Active** switch

### Option B: Daily Sync

1. Add **Schedule Trigger**
2. Configure:
   ```
   Trigger Interval: Days
   Days Between Triggers: 1
   Trigger at Hour: 2 (2 AM)
   Trigger at Minute: 0
   ```
3. Connect and activate

---

## Part 6: Analyze Your Data in Google Sheets

### Create a Pivot Table

1. **Select all data**: Click A1 → Ctrl+Shift+End
2. **Insert → Pivot table**
3. **Example: Sales by Organization**
   - Rows: SalesOrganization
   - Values: SalesOrder (COUNTA), TotalAmount (SUM)
4. **Create chart** from pivot table

### Add Filters

1. **Select header row**
2. **Data → Create a filter**
3. **Filter by**:
   - Date range
   - Sales organization
   - Customer
   - Status

### Calculate Metrics

Add columns for:
- **Days to Delivery**: `=L2-C2` (RequestedDeliveryDate - SalesOrderDate)
- **Status Color**: Use conditional formatting
- **Month**: `=TEXT(C2,"MMMM YYYY")`

---

## Part 7: Share with Your Team

### Share the Sheet

1. Click **Share** button (top-right)
2. Enter team members' emails
3. Set permissions:
   - **Viewer**: Can only view
   - **Commenter**: Can add comments
   - **Editor**: Can edit (be careful!)
4. Click **Send**

### Create Dashboard

1. **Create new sheet tab**: Click **+** at bottom
2. Name it: **Dashboard**
3. Add:
   - Total sales: `=SUM(Sheet1!J:J)`
   - Total orders: `=COUNTA(Sheet1!A:A)-1`
   - Average order value: `=AVERAGE(Sheet1!J:J)`
   - Charts from pivot tables

---

## Part 8: Advanced Features

### Prevent Duplicates

The workflow uses `SalesOrder` as matching column:
- **First run**: Adds all orders
- **Subsequent runs**: Updates existing orders, adds new ones
- No duplicate rows!

### Add Email Notifications

1. **Add Email node** after "Sync Summary"
2. Configure:
   ```
   To: your-email@example.com
   Subject: S/4HANA Sync Complete
   Message: {{ $json.message }}
   ```

### Filter Sales Orders

Modify the URL in Node 2 to add OData filters:

**Only recent orders (last 30 days):**
```
https://49.206.196.74:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view?$format=json&$filter=SalesOrderDate ge datetime'2025-10-21T00:00:00'&$top=1000
```

**Specific sales organization:**
```
&$filter=SalesOrganization eq '2510'
```

---

## Workflow Diagram

```
┌──────────────────┐
│ Schedule Trigger │ → Runs every hour/day
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Fetch from S/4HANA              │
│ https://49.206.196.74:8009      │
│ Auth: s4gui4/Sap@123456         │
└────────┬────────────────────────┘
         │
         │ JSON (OData format)
         │
         ▼
┌─────────────────────────────────┐
│ Transform Data                  │
│ - Parse SAP dates               │
│ - Format for Google Sheets      │
│ - Clean field names             │
└────────┬────────────────────────┘
         │
         │ Structured rows
         │
         ▼
┌─────────────────────────────────┐
│ Append to Google Sheets         │
│ - Match on SalesOrder           │
│ - Update existing rows          │
│ - Add new rows                  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Google Sheets                   │
│ "S/4HANA Sales Orders"          │
│ - Easy filtering                │
│ - Pivot tables                  │
│ - Share with team               │
└─────────────────────────────────┘
```

---

## Troubleshooting

### Error: "Could not find sheet"

**Solution**: 
1. In "Append to Google Sheets" node
2. Click **Document** dropdown → Refresh
3. Select your sheet from the list

### Error: "Column mismatch"

**Solution**: 
1. Verify Google Sheets has exact column names (case-sensitive)
2. Check for extra spaces in headers
3. Delete any extra columns

### No data appearing

**Solution**:
1. Check execution log in n8n
2. Verify S/4HANA node returned data
3. Check Transform node output
4. Ensure Google Sheets credential is valid

### Duplicate rows appearing

**Solution**:
1. In "Append to Google Sheets" node
2. Verify **Matching Column** is set to `SalesOrder`
3. Operation should be **Append or Update**

---

## Summary Checklist

- [ ] Google Sheet created with headers
- [ ] Google Sheets OAuth credential added to n8n
- [ ] Workflow imported and configured
- [ ] S/4HANA credential selected
- [ ] Google Sheet selected in workflow
- [ ] Test run completed successfully
- [ ] Data visible in Google Sheets
- [ ] Schedule trigger added (optional)
- [ ] Workflow activated
- [ ] Sheet shared with team (optional)

---

## Benefits of Google Sheets Approach

✅ **No Database Setup**: Works immediately, no PostgreSQL configuration
✅ **Easy Sharing**: Share with anyone via email
✅ **Built-in Analytics**: Pivot tables, charts, filters
✅ **Familiar Interface**: Everyone knows Google Sheets
✅ **Free**: No database hosting costs
✅ **Mobile Access**: View on phone/tablet
✅ **Collaboration**: Multiple people can view/comment
✅ **Version History**: See changes over time

---

## Next Steps

1. **Import the workflow**: `n8n-s4hana-to-google-sheets.json`
2. **Connect Google account**: Add OAuth credential
3. **Select your sheet**: In the workflow node
4. **Run test**: Execute once manually
5. **Activate**: Turn on for automatic syncing

Your S/4HANA sales orders will now automatically sync to Google Sheets! 📊
