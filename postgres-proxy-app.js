// Simple PostgreSQL proxy for n8n Cloud
// This allows n8n Cloud to connect to your SAP BTP PostgreSQL

const express = require('express');
const { Pool } = require('pg');
const app = express();

app.use(express.json());

// Get PostgreSQL connection from Cloud Foundry VCAP_SERVICES
const vcapServices = JSON.parse(process.env.VCAP_SERVICES || '{}');
const postgresService = vcapServices['postgresql-db'][0];
const credentials = postgresService.credentials;

const pool = new Pool({
  host: credentials.hostname,
  port: credentials.port,
  database: credentials.dbname,
  user: credentials.username,
  password: credentials.password,
  ssl: { rejectUnauthorized: false }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', database: 'connected' });
});

// Execute query endpoint
app.post('/query', async (req, res) => {
  const { sql, params } = req.body;
  
  try {
    const result = await pool.query(sql, params);
    res.json({
      rows: result.rows,
      rowCount: result.rowCount
    });
  } catch (error) {
    res.status(500).json({
      error: error.message,
      detail: error.detail
    });
  }
});

// Get sales orders (specific endpoint for n8n)
app.get('/sales-orders', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM sales_orders ORDER BY fetched_at DESC LIMIT 100');
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Insert sales order (for n8n to call)
app.post('/sales-orders', async (req, res) => {
  const order = req.body;
  
  const sql = `
    INSERT INTO sales_orders (
      sales_order, sales_order_type, created_by_user, last_changed_by_user,
      creation_date, sales_organization, distribution_channel, organization_division,
      sold_to_party, customer_group, sales_order_date, purchase_order_by_customer,
      total_net_amount, transaction_currency, fetched_at
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
    ON CONFLICT (sales_order) DO UPDATE SET
      sales_order_type = EXCLUDED.sales_order_type,
      last_changed_by_user = EXCLUDED.last_changed_by_user,
      total_net_amount = EXCLUDED.total_net_amount,
      updated_at = CURRENT_TIMESTAMP
    RETURNING *
  `;
  
  const values = [
    order.sales_order,
    order.sales_order_type,
    order.created_by_user,
    order.last_changed_by_user,
    order.creation_date,
    order.sales_organization,
    order.distribution_channel,
    order.organization_division,
    order.sold_to_party,
    order.customer_group,
    order.sales_order_date,
    order.purchase_order_by_customer,
    order.total_net_amount,
    order.transaction_currency,
    order.fetched_at || new Date().toISOString()
  ];
  
  try {
    const result = await pool.query(sql, values);
    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`PostgreSQL Proxy running on port ${PORT}`);
});
