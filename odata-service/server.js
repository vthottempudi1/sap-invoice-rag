const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// Sample product data
const products = [
  { ID: 1, Name: 'Laptop', Description: 'High performance laptop', Price: 1299.99, Category: 'Electronics' },
  { ID: 2, Name: 'Mouse', Description: 'Wireless mouse', Price: 29.99, Category: 'Electronics' },
  { ID: 3, Name: 'Keyboard', Description: 'Mechanical keyboard', Price: 89.99, Category: 'Electronics' },
  { ID: 4, Name: 'Monitor', Description: '27 inch 4K monitor', Price: 399.99, Category: 'Electronics' },
  { ID: 5, Name: 'Desk', Description: 'Standing desk', Price: 499.99, Category: 'Furniture' }
];

// OData service document
app.get('/odata/v4/', (req, res) => {
  res.json({
    '@odata.context': '$metadata',
    value: [
      {
        name: 'Products',
        kind: 'EntitySet',
        url: 'Products'
      }
    ]
  });
});

// OData metadata
app.get('/odata/v4/$metadata', (req, res) => {
  res.set('Content-Type', 'application/xml');
  res.send(`<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="CatalogService">
      <EntityType Name="Product">
        <Key>
          <PropertyRef Name="ID"/>
        </Key>
        <Property Name="ID" Type="Edm.Int32" Nullable="false"/>
        <Property Name="Name" Type="Edm.String"/>
        <Property Name="Description" Type="Edm.String"/>
        <Property Name="Price" Type="Edm.Decimal"/>
        <Property Name="Category" Type="Edm.String"/>
      </EntityType>
      <EntityContainer Name="EntityContainer">
        <EntitySet Name="Products" EntityType="CatalogService.Product"/>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>`);
});

// Get all products with OData query support
app.get('/odata/v4/Products', (req, res) => {
  let result = [...products];
  
  // Handle $filter
  if (req.query.$filter) {
    const filter = req.query.$filter;
    if (filter.includes('Price gt')) {
      const price = parseFloat(filter.split('Price gt')[1].trim());
      result = result.filter(p => p.Price > price);
    }
    if (filter.includes('Category eq')) {
      const category = filter.split("'")[1];
      result = result.filter(p => p.Category === category);
    }
  }
  
  // Handle $select
  if (req.query.$select) {
    const fields = req.query.$select.split(',').map(f => f.trim());
    result = result.map(item => {
      const newItem = {};
      fields.forEach(field => {
        if (item[field] !== undefined) newItem[field] = item[field];
      });
      return newItem;
    });
  }
  
  // Handle $top
  if (req.query.$top) {
    result = result.slice(0, parseInt(req.query.$top));
  }
  
  // Handle $skip
  if (req.query.$skip) {
    result = result.slice(parseInt(req.query.$skip));
  }
  
  res.json({
    '@odata.context': '/odata/v4/$metadata#Products',
    value: result
  });
});

// Get single product
app.get('/odata/v4/Products/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const product = products.find(p => p.ID === id);
  
  if (product) {
    res.json({
      '@odata.context': '/odata/v4/$metadata#Products/$entity',
      ...product
    });
  } else {
    res.status(404).json({ error: 'Product not found' });
  }
});

// Health check
app.get('/', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'SAP OData Mock Service',
    endpoints: [
      '/odata/v4/',
      '/odata/v4/$metadata',
      '/odata/v4/Products'
    ]
  });
});

app.listen(port, () => {
  console.log(`OData service listening on port ${port}`);
});
