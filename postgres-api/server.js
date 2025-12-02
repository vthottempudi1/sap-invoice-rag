const express = require('express');
const { Client } = require('pg');
const app = express();
const port = process.env.PORT || 3001;

app.use(express.json());

// PostgreSQL connection configuration
const getClient = () => {
  const vcapServices = JSON.parse(process.env.VCAP_SERVICES || '{}');
  const postgresService = vcapServices['postgresql-db']?.[0];
  
  if (postgresService) {
    // Use bound service credentials
    const credentials = postgresService.credentials;
    return new Client({
      host: credentials.hostname,
      port: credentials.port,
      database: credentials.dbname,
      user: credentials.username,
      password: credentials.password,
      ssl: { rejectUnauthorized: false }
    });
  } else {
    // Fallback to manual configuration
    return new Client({
      host: process.env.DB_HOST,
      port: process.env.DB_PORT,
      database: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      ssl: { rejectUnauthorized: false }
    });
  }
};

// Health check
app.get('/', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'PostgreSQL Proxy API',
    endpoints: [
      'POST /api/products - Insert/Update products',
      'GET /api/products - Get all products',
      'GET /api/products/:id - Get product by ID',
      'DELETE /api/products/:id - Delete product'
    ]
  });
});

// Insert or update products (UPSERT)
app.post('/api/products', async (req, res) => {
  const client = getClient();
  
  try {
    await client.connect();
    
    const products = Array.isArray(req.body) ? req.body : [req.body];
    const results = [];
    
    for (const product of products) {
      const query = `
        INSERT INTO products (product_id, product_name, category, price, fetched_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (product_id) DO UPDATE SET
          product_name = EXCLUDED.product_name,
          category = EXCLUDED.category,
          price = EXCLUDED.price,
          fetched_at = EXCLUDED.fetched_at,
          updated_at = CURRENT_TIMESTAMP
        RETURNING *;
      `;
      
      const values = [
        product.ProductID,
        product.ProductName,
        product.Category,
        product.Price,
        product.FetchedAt || new Date().toISOString()
      ];
      
      const result = await client.query(query, values);
      results.push(result.rows[0]);
    }
    
    res.json({ 
      success: true, 
      message: `${results.length} products processed`,
      data: results 
    });
    
  } catch (error) {
    console.error('Error inserting products:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  } finally {
    await client.end();
  }
});

// Get all products
app.get('/api/products', async (req, res) => {
  const client = getClient();
  
  try {
    await client.connect();
    const result = await client.query('SELECT * FROM products ORDER BY product_id');
    
    res.json({ 
      success: true, 
      count: result.rows.length,
      data: result.rows 
    });
    
  } catch (error) {
    console.error('Error fetching products:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  } finally {
    await client.end();
  }
});

// Get product by ID
app.get('/api/products/:id', async (req, res) => {
  const client = getClient();
  
  try {
    await client.connect();
    const result = await client.query(
      'SELECT * FROM products WHERE product_id = $1',
      [req.params.id]
    );
    
    if (result.rows.length === 0) {
      res.status(404).json({ 
        success: false, 
        message: 'Product not found' 
      });
    } else {
      res.json({ 
        success: true, 
        data: result.rows[0] 
      });
    }
    
  } catch (error) {
    console.error('Error fetching product:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  } finally {
    await client.end();
  }
});

// Delete product
app.delete('/api/products/:id', async (req, res) => {
  const client = getClient();
  
  try {
    await client.connect();
    const result = await client.query(
      'DELETE FROM products WHERE product_id = $1 RETURNING *',
      [req.params.id]
    );
    
    if (result.rows.length === 0) {
      res.status(404).json({ 
        success: false, 
        message: 'Product not found' 
      });
    } else {
      res.json({ 
        success: true, 
        message: 'Product deleted',
        data: result.rows[0] 
      });
    }
    
  } catch (error) {
    console.error('Error deleting product:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  } finally {
    await client.end();
  }
});

// Initialize database table
app.post('/api/init-db', async (req, res) => {
  const client = getClient();
  
  try {
    await client.connect();
    
    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        price DECIMAL(10, 2),
        fetched_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
      
      CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
      CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
    `;
    
    await client.query(createTableQuery);
    
    res.json({ 
      success: true, 
      message: 'Database initialized successfully' 
    });
    
  } catch (error) {
    console.error('Error initializing database:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  } finally {
    await client.end();
  }
});

app.listen(port, () => {
  console.log(`PostgreSQL Proxy API listening on port ${port}`);
});
