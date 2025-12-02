# n8n Cloud PostgreSQL Connection Setup

## PostgreSQL Credential Configuration

In your n8n Cloud instance (vthottempudi1.app.n8n.cloud), create a PostgreSQL credential with these **EXACT** values:

### Connection Details
```
Host: postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com
Port: 6974
Database: XMCMDsOblizg
User: 30b40be4db3f
Password: e694313dfb09a85a0f5
```

### SSL Configuration
- **SSL Mode**: `require` (or `verify-ca` if available)
- **SSL Certificate**: Leave empty (AWS RDS handles this)

## Step-by-Step Setup

### 1. Create PostgreSQL Credential in n8n Cloud

1. Go to https://vthottempudi1.app.n8n.cloud
2. Click your profile icon → **Settings** → **Credentials**
3. Click **+ Add Credential**
4. Search for and select **Postgres**
5. Fill in the connection details:
   ```
   Connection Type: Connection Parameters
   Host: postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com
   Port: 6974
   Database: XMCMDsOblizg
   User: 30b40be4db3f
   Password: e694313dfb09a85a0f5
   SSL Mode: require
   ```
6. **Important**: Ensure there are NO spaces before/after any values
7. Click **Save**
8. Click **Test Connection** to verify

### 2. Common Issues & Solutions

#### Issue: "Connection cannot be established"
**Solution**: Verify the hostname is EXACTLY:
```
postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com
```
- Must include `.cqryblsdrbcs.us-east-1.rds.amazonaws.com`
- No `https://` prefix
- No trailing spaces

#### Issue: "SSL connection error"
**Solution**: Set SSL Mode to `require` (not `disable`)

#### Issue: "Connection timeout"
**Solution**: 
- Verify port is `6974` (not 5432)
- Check SAP BTP PostgreSQL service is running:
  ```bash
  cf service n8n-database
  ```

#### Issue: "Database does not exist"
**Solution**: Database name is case-sensitive: `XMCMDsOblizg` (not `xmcmdsoblizg`)

### 3. Test Connection with Simple Query

After creating the credential:

1. Create a new workflow or use existing one
2. Add a **Postgres** node
3. Select your credential
4. Set Operation: **Execute Query**
5. Query:
   ```sql
   SELECT version();
   ```
6. Execute the node

Expected output:
```
PostgreSQL 14.x on x86_64-pc-linux-gnu...
```

### 4. Create Sales Orders Table

Once connection is verified, run this SQL:

```sql
CREATE TABLE IF NOT EXISTS sales_orders (
    sales_order VARCHAR(10) PRIMARY KEY,
    sales_order_type VARCHAR(4),
    created_by_user VARCHAR(12),
    last_changed_by_user VARCHAR(12),
    creation_date TIMESTAMP,
    sales_organization VARCHAR(4),
    distribution_channel VARCHAR(2),
    organization_division VARCHAR(2),
    sold_to_party VARCHAR(10),
    customer_group VARCHAR(2),
    sales_order_date TIMESTAMP,
    purchase_order_by_customer VARCHAR(35),
    total_net_amount DECIMAL(15,2),
    transaction_currency VARCHAR(5),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales_orders(sales_order_date);
CREATE INDEX IF NOT EXISTS idx_customer ON sales_orders(sold_to_party);
CREATE INDEX IF NOT EXISTS idx_created_by ON sales_orders(created_by_user);
```

### 5. Import S/4HANA to PostgreSQL Workflow

1. Go to your n8n Cloud workflows
2. Click **+ Add Workflow**
3. Click the **⋮** menu → **Import from File**
4. Select `n8n-s4hana-sales-to-postgres.json` from your local workspace
5. Update the workflow:
   - **HTTP Request node**: Link your S/4HANA Basic Auth credential (s4gui4/Sap@123456)
   - **Postgres node**: Link your newly created PostgreSQL credential
6. Execute the workflow to sync data

## Verification

After workflow executes successfully:

```sql
-- Check if data was imported
SELECT COUNT(*) FROM sales_orders;

-- View recent sales orders
SELECT sales_order, sales_order_date, sold_to_party, total_net_amount, transaction_currency
FROM sales_orders
ORDER BY sales_order_date DESC
LIMIT 10;
```

## Connection String Format (for reference)

If you need to use a connection string format:
```
postgresql://30b40be4db3f:e694313dfb09a85a0f5@postgres-e96ae2c4-8eb7-42bd-9ece-c5c50432af22.cqryblsdrbcs.us-east-1.rds.amazonaws.com:6974/XMCMDsOblizg?sslmode=require
```

## Troubleshooting Checklist

- [ ] Hostname includes full AWS RDS domain
- [ ] Port is 6974 (not 5432)
- [ ] Database name is case-sensitive: `XMCMDsOblizg`
- [ ] SSL mode is set to `require`
- [ ] No spaces in any credential fields
- [ ] SAP BTP PostgreSQL service is active (check with `cf service n8n-database`)
- [ ] n8n Cloud IP is whitelisted (usually automatic for AWS RDS)

## Next Steps

1. ✅ Create PostgreSQL credential in n8n Cloud
2. ✅ Test connection with `SELECT version()`
3. ✅ Create `sales_orders` table
4. ✅ Import and execute S/4HANA sync workflow
5. Schedule workflow to run automatically (hourly/daily)
