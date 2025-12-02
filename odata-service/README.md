# SAP OData V4 Mock Service

A simple OData V4 service for testing with n8n workflows.

## Features
- OData V4 compliant endpoints
- Product catalog with 5 sample products
- Query support: $filter, $select, $top, $skip
- Metadata endpoint

## Endpoints

### Service Document
```
GET /odata/v4/
```

### Metadata
```
GET /odata/v4/$metadata
```

### Products Collection
```
GET /odata/v4/Products
```

### Query Examples

Get all products:
```
GET /odata/v4/Products
```

Filter by price:
```
GET /odata/v4/Products?$filter=Price gt 100
```

Select specific fields:
```
GET /odata/v4/Products?$select=ID,Name,Price
```

Top 3 products:
```
GET /odata/v4/Products?$top=3
```

Combined query:
```
GET /odata/v4/Products?$filter=Price gt 50&$select=Name,Price&$top=5
```

## Deploy to SAP BTP Cloud Foundry

1. Install dependencies:
```bash
npm install
```

2. Login to Cloud Foundry:
```bash
cf login
```

3. Push the application:
```bash
cf push
```

4. Get the application URL:
```bash
cf apps
```

## Local Development

Run locally:
```bash
npm install
npm start
```

Service will be available at: http://localhost:3000

## Sample Data

The service includes 5 products:
- Laptop ($1299.99)
- Mouse ($29.99)
- Keyboard ($89.99)
- Monitor ($399.99)
- Desk ($499.99)
