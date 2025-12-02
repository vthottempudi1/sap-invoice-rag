# Complete Guide: Connect n8n Cloud to SAP S/4HANA

## Overview
This guide shows you how to sync sales order data from SAP S/4HANA to SAP BTP PostgreSQL using n8n Cloud (trial version).

**Your Environment:**
- **n8n Cloud**: vthottempudi1.app.n8n.cloud
- **S/4HANA System**: s4hana2020.support.com:8009 (publicly accessible via HTTPS)
- **OData Service**: ZSALE_SERVICE/zsales_view (confirmed working)
- **Database**: SAP BTP PostgreSQL on AWS RDS

---

## Part 1: Create PostgreSQL Table

### Step 1.1: Connect to PostgreSQL Database

You'll need to create the `sales_orders` table in your PostgreSQL database first.

**Option A: Using pgAdmin or DBeaver**
1. Download [pgAdmin](https://www.pgadmin.org/download/) or [DBeaver](https://dbeaver.io/download/)
2. Create new PostgreSQL connection with these details:

```
Host: postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com
Port: 6974
Database: XMCMDsOblizg
Username: 7842af8b9020
Password: c7b61e26789d9b8a32e285396b749a29
SSL Mode: Require
```

**Option B: Using Cloud Foundry CLI**
```powershell
# Install cf-conduit plugin if not already installed
cf install-plugin conduit

# Create SSH tunnel to PostgreSQL
cf conduit n8n-database -- psql
```

### Step 1.2: Create the Table

Run this SQL script in your PostgreSQL client:

```sql
-- Create sales_orders table
CREATE TABLE IF NOT EXISTS sales_orders (
    sales_order VARCHAR(10) PRIMARY KEY,
    sales_order_type VARCHAR(4),
    created_by_user VARCHAR(12),
    last_changed_by_user VARCHAR(12),
    creation_date DATE,
    sales_organization VARCHAR(4),
    distribution_channel VARCHAR(2),
    organization_division VARCHAR(2),
    sold_to_party VARCHAR(10),
    customer_group VARCHAR(2),
    sales_order_date DATE,
    purchase_order_by_customer VARCHAR(35),
    total_net_amount DECIMAL(15, 2),
    transaction_currency VARCHAR(5),
    fetched_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better query performance
CREATE INDEX idx_sales_order_date ON sales_orders(sales_order_date);
CREATE INDEX idx_sales_organization ON sales_orders(sales_organization);

-- Verify table creation
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sales_orders'
ORDER BY ordinal_position;
```

---

## Part 2: Configure n8n Cloud Credentials

### Step 2.1: Create S/4HANA Basic Auth Credential

1. **Open n8n Cloud**: https://vthottempudi1.app.n8n.cloud
2. **Navigate to Credentials**:
   - Click your profile icon (top-right)
   - Select **Credentials**
3. **Add New Credential**:
   - Click **+ Add Credential**
   - Search for **HTTP Basic Auth**
   - Fill in:
     ```
     Credential Name: S/4HANA Basic Auth
     Username: s4gui4
     Password: Sap@123456
     ```
   - Click **Save**

### Step 2.2: Create PostgreSQL Credential

1. **In Credentials page**, click **+ Add Credential**
2. **Search for**: Postgres
3. **Fill in Connection Details**:
   ```
   Credential Name: SAP BTP PostgreSQL
   Host: postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com
   Port: 6974
   Database: XMCMDsOblizg
   User: 7842af8b9020
   Password: c7b61e26789d9b8a32e285396b749a29
   SSL: Enable
   ```
4. **Test Connection**: Click **Test Credential** button
5. **Save** if test is successful

> **Important**: If the test fails with "connection cannot be established", your PostgreSQL credentials may have rotated. Get fresh credentials by running:
> ```powershell
> cf service-key n8n-database n8n-cloud-key
> ```

---

## Part 3: Import and Configure Workflow

### Step 3.1: Import Workflow

1. **Download Workflow File**: `n8n-s4hana-direct-connection.json` (created in this folder)

2. **Import into n8n Cloud**:
   - In n8n Cloud, click **Workflows** (left sidebar)
   - Click **+ Add Workflow**
   - Click **Import from File**
   - Select `n8n-s4hana-direct-connection.json`
   - Click **Import**

### Step 3.2: Configure Workflow Nodes

The workflow has **5 nodes**:

#### **Node 1: Manual Trigger**
- No configuration needed
- Used to start the workflow manually

#### **Node 2: Fetch Sales Orders from S/4HANA**
- **Type**: HTTP Request
- **Settings**:
  ```
  Authentication: Generic Credential Type > HTTP Basic Auth
  Credential: S/4HANA Basic Auth (select from dropdown)
  Method: GET
  URL: https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view
  ```
- **Headers**:
  ```
  Accept: application/json
  ```
- **Options**:
  ```
  Allow Unauthorized Certificates: ✓ (checked)
  Timeout: 30000 (milliseconds)
  ```

#### **Node 3: Parse and Transform Sales Orders**
- **Type**: Code
- **Purpose**: Converts OData JSON format to PostgreSQL-ready format
- No configuration needed (code is pre-written)

#### **Node 4: Save to PostgreSQL**
- **Type**: Postgres
- **Settings**:
  ```
  Credential: SAP BTP PostgreSQL (select from dropdown)
  Operation: Execute Query
  ```
- **Query**: Pre-configured INSERT with UPSERT logic (ON CONFLICT DO UPDATE)
- This ensures:
  - New sales orders are inserted
  - Existing sales orders are updated if data changes

#### **Node 5: Sync Summary**
- **Type**: Code
- **Purpose**: Generates summary message with sync statistics
- No configuration needed

---

## Part 4: Test the Workflow

### Step 4.1: Manual Test Run

1. **Open the Workflow** in n8n Cloud editor
2. **Click "Execute Workflow"** button (top-right, play icon)
3. **Watch the Execution**:
   - Node 1 (Manual Trigger): ✓ Activated
   - Node 2 (Fetch Sales Orders): Should retrieve ~14 sales orders
   - Node 3 (Parse): Should transform OData to database format
   - Node 4 (Save to PostgreSQL): Should insert/update records
   - Node 5 (Summary): Shows sync statistics

### Step 4.2: Verify Data in PostgreSQL

Run this query in your PostgreSQL client:

```sql
-- Check total records
SELECT COUNT(*) as total_sales_orders FROM sales_orders;

-- View recent sales orders
SELECT 
    sales_order,
    sales_order_date,
    sold_to_party,
    total_net_amount,
    transaction_currency,
    fetched_at
FROM sales_orders
ORDER BY fetched_at DESC
LIMIT 10;

-- Verify specific sales order
SELECT * FROM sales_orders WHERE sales_order = '1';
```

**Expected Results**:
- Should see 14 sales orders (IDs: 1, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94)
- Each record should have complete data (sales org, customer, amounts, etc.)

---

## Part 5: Schedule Automatic Sync

### Step 5.1: Add Schedule Trigger

1. **In Workflow Editor**, click **+** button (add node)
2. **Search for**: Schedule Trigger
3. **Configure Schedule**:
   ```
   Trigger Interval: Hours
   Hours Between Triggers: 1
   ```
   Or for daily sync:
   ```
   Trigger Interval: Days
   Days Between Triggers: 1
   Trigger at Hour: 2 (2 AM)
   Trigger at Minute: 0
   ```

4. **Connect Schedule Trigger** to "Fetch Sales Orders from S/4HANA" node
5. **Keep Manual Trigger** for on-demand syncs

### Step 5.2: Activate Workflow

1. **Click "Active" toggle** (top-right, next to workflow name)
2. Status should change to **Active** (green)
3. Workflow will now run automatically on schedule

---

## Part 6: Monitoring and Troubleshooting

### View Execution History

1. **Navigate to Executions** (left sidebar)
2. **View Past Runs**:
   - Successful executions: Green checkmark
   - Failed executions: Red X
3. **Click any execution** to see detailed logs

### Common Issues and Solutions

#### Issue 1: "Could not resolve host: s4hana2020.support.com"
**Solution**: n8n Cloud cannot resolve the hostname. S/4HANA system might be internal-only.

**Fix Options**:
1. **Use IP Address**: Change URL to `https://49.206.196.74:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view`
2. **Add Header**: In HTTP Request node, add header:
   ```
   Host: s4hana2020.support.com
   ```

#### Issue 2: "SSL Certificate Error"
**Cause**: Self-signed certificate on S/4HANA

**Solution**: Ensure "Allow Unauthorized Certificates" is checked in HTTP Request node options

#### Issue 3: "401 Unauthorized"
**Cause**: Invalid credentials or session timeout

**Solution**:
1. Verify credentials: s4gui4 / Sap@123456
2. Test credentials with curl:
   ```powershell
   curl.exe -k -u s4gui4:Sap@123456 https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view
   ```

#### Issue 4: "PostgreSQL Connection Timeout"
**Cause**: Credentials rotated or network issue

**Solution**: Get fresh credentials:
```powershell
cf service-key n8n-database n8n-cloud-key
```
Update credential in n8n Cloud with new username/password.

#### Issue 5: "Empty Response from S/4HANA"
**Cause**: No data in zsales_view or filter applied

**Solution**: 
1. Add `$top=100` parameter to URL to increase limit
2. Full URL: `https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view?$top=100`

---

## Part 7: Advanced Enhancements

### Add Filters to Fetch Recent Orders Only

Modify HTTP Request URL to include OData filters:

```
https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view?$filter=SalesOrderDate ge datetime'2025-01-01T00:00:00'&$top=1000
```

### Add Error Notifications

1. **Add "Slack" or "Email" node** after "Save to PostgreSQL"
2. **Configure to send on error**:
   - In workflow settings, click "Settings" → "Error Workflow"
   - Create separate error handling workflow

### Add Data Validation

Insert a "Code" node between "Parse" and "Save" to validate data:

```javascript
// Validate sales orders before saving
const items = $input.all();

const validItems = items.filter(item => {
  const order = item.json;
  
  // Check required fields
  if (!order.sales_order || !order.sales_order_type) {
    console.error('Missing required fields:', order);
    return false;
  }
  
  // Validate amount
  if (order.total_net_amount < 0) {
    console.error('Invalid amount:', order);
    return false;
  }
  
  return true;
});

return validItems;
```

---

## Part 8: Query Examples for Analysis

Once data is synced, run these queries for business insights:

### Sales by Organization
```sql
SELECT 
    sales_organization,
    COUNT(*) as total_orders,
    SUM(total_net_amount) as total_revenue,
    AVG(total_net_amount) as avg_order_value
FROM sales_orders
GROUP BY sales_organization
ORDER BY total_revenue DESC;
```

### Sales Trend by Date
```sql
SELECT 
    DATE(sales_order_date) as order_date,
    COUNT(*) as orders_count,
    SUM(total_net_amount) as daily_revenue
FROM sales_orders
WHERE sales_order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(sales_order_date)
ORDER BY order_date;
```

### Top Customers
```sql
SELECT 
    sold_to_party as customer_id,
    COUNT(*) as total_orders,
    SUM(total_net_amount) as total_spent,
    MAX(sales_order_date) as last_order_date
FROM sales_orders
GROUP BY sold_to_party
ORDER BY total_spent DESC
LIMIT 10;
```

---

## Workflow Architecture Diagram

```
┌─────────────────────┐
│  n8n Cloud          │
│  (Trial Version)    │
└──────────┬──────────┘
           │
           │ 1. Schedule Trigger (Every Hour)
           │ 2. Manual Trigger (On-Demand)
           │
           ▼
┌─────────────────────────────────────────┐
│  HTTP Request Node                      │
│  ─────────────────                      │
│  GET https://s4hana2020.support.com:... │
│  Auth: Basic (s4gui4/Sap@123456)        │
│  SSL: Allow Unauthorized Certs          │
└──────────┬──────────────────────────────┘
           │
           │ OData JSON Response
           │
           ▼
┌─────────────────────────────────────────┐
│  Code Node: Parse & Transform           │
│  ───────────────────────────────        │
│  - Extract d.results array              │
│  - Map OData fields to DB columns       │
│  - Format dates and numbers             │
└──────────┬──────────────────────────────┘
           │
           │ Array of Sales Orders
           │
           ▼
┌─────────────────────────────────────────┐
│  PostgreSQL Node                        │
│  ────────────────                       │
│  INSERT ... ON CONFLICT DO UPDATE       │
│  (UPSERT logic for idempotency)         │
└──────────┬──────────────────────────────┘
           │
           │ Insert/Update Results
           │
           ▼
┌─────────────────────────────────────────┐
│  Code Node: Sync Summary                │
│  ────────────────────────               │
│  Generate statistics and completion msg │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  SAP BTP PostgreSQL                     │
│  AWS RDS (US-East-1)                    │
│  Table: sales_orders                    │
└─────────────────────────────────────────┘
```

---

## Summary Checklist

- [ ] PostgreSQL table `sales_orders` created
- [ ] S/4HANA Basic Auth credential configured in n8n Cloud
- [ ] PostgreSQL credential configured in n8n Cloud
- [ ] Workflow imported: `n8n-s4hana-direct-connection.json`
- [ ] All 5 nodes configured with correct credentials
- [ ] Manual test execution successful
- [ ] Data verified in PostgreSQL database
- [ ] Schedule trigger added and configured
- [ ] Workflow activated (green toggle)
- [ ] First scheduled run completed successfully

---

## Support and Resources

**Test S/4HANA Connection**:
```powershell
# From your Windows machine
curl.exe -k -u s4gui4:Sap@123456 https://s4hana2020.support.com:8009/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view
```

**Get Fresh PostgreSQL Credentials**:
```powershell
cf service-key n8n-database n8n-cloud-key
```

**Check n8n Cloud Status**:
- Dashboard: https://vthottempudi1.app.n8n.cloud
- Workflows: https://vthottempudi1.app.n8n.cloud/workflows
- Executions: https://vthottempudi1.app.n8n.cloud/executions

**Your Working Environment**:
- S/4HANA: ✓ Public HTTPS (no VPN/Cloud Connector needed)
- n8n Cloud: ✓ Trial version active
- PostgreSQL: ✓ SAP BTP Trial (AWS RDS)
- Authentication: ✓ Basic Auth confirmed working

---

## Next Steps

1. **Import the workflow** (`n8n-s4hana-direct-connection.json`)
2. **Configure credentials** (5 minutes)
3. **Run test execution** (verify 14 sales orders synced)
4. **Activate workflow** for automatic hourly sync
5. **Monitor executions** in n8n Cloud dashboard

**Need Help?** Check the troubleshooting section above or test connections using the provided curl commands.
