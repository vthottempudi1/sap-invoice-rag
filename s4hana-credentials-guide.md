# S/4HANA Basic Auth Setup in n8n

## Credentials
- **Username**: `s4gui4`
- **Password**: `Sap@123456`

## Setup Steps in n8n

1. Open n8n at `http://localhost:5678`
2. Login with `admin` / `your-secure-password`
3. Click **Settings** (gear icon) in the left sidebar
4. Click **Credentials**
5. Click **Add Credential** button
6. Search for "**Basic Auth**"
7. Fill in the following:
   - **Credential Name**: `S/4HANA Basic Auth`
   - **User**: `s4gui4`
   - **Password**: `Sap@123456`
8. Click **Save**

## Using in HTTP Request Nodes

When creating workflows that call S/4HANA OData services:

1. Add **HTTP Request** node
2. Set **Authentication** to "Predefined Credential Type"
3. Select **Credential Type**: "Basic Auth"
4. Select **Credential**: "S/4HANA Basic Auth"
5. Configure your S/4HANA endpoint URL, e.g.:
   - `https://your-s4hana-system.com/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner`

## Example Workflow Node Configuration

```json
{
  "parameters": {
    "method": "GET",
    "url": "https://your-s4hana-system.com/sap/opu/odata/sap/API_SERVICE/EntitySet",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "basicAuth",
    "options": {
      "headers": {
        "Accept": "application/json"
      }
    }
  },
  "type": "n8n-nodes-base.httpRequest",
  "credentials": {
    "basicAuth": {
      "id": "1",
      "name": "S/4HANA Basic Auth"
    }
  }
}
```

## Workflow: S/4HANA OData Integration

Import the workflow: `n8n-s4hana-odata-workflow.json`

### Workflow Features

**1. Basic Auth Credentials**
- All HTTP Request nodes use "S/4HANA Basic Auth" credential
- Username: `s4gui4`
- Password: `Sap@123456`

**2. HTTP Request Nodes**
- **Read Business Partners (GET)**: Fetches top 10 business partners
- **Fetch CSRF Token**: Gets CSRF token for write operations
- **Create Business Partner (POST)**: Creates new business partner
- **Update Business Partner (PATCH)**: Updates existing business partner
- **Delete Business Partner (DELETE)**: Deletes business partner

**3. CSRF Token Handling**
- **Fetch CSRF Token** node: Sends GET request with `X-CSRF-Token: Fetch` header
- **Extract CSRF & Cookies** node: Extracts token and cookies from response headers
- **Create/Update/Delete** nodes: Include CSRF token and cookies in headers

### CSRF Token Flow

```
1. GET request with X-CSRF-Token: Fetch header
   ↓
2. S/4HANA returns CSRF token in response header
   ↓
3. Extract token from headers['x-csrf-token']
   ↓
4. Include token in POST/PATCH/DELETE requests
```

### Important Configuration

Before using the workflow, update these URLs with your actual S/4HANA system:

- Replace `https://your-s4hana-system.com` with your S/4HANA base URL
- Example: `https://s4hana-dev.mycompany.com` or `https://my300123.s4hana.ondemand.com`

### Testing Steps

1. **Test Read Operation (No CSRF needed)**:
   - Execute "Read Business Partners (GET)" node
   - Should return list of business partners

2. **Test Create Operation (CSRF required)**:
   - Execute "Fetch CSRF Token" → "Extract CSRF & Cookies" → "Create Business Partner (POST)"
   - Verify new business partner is created

3. **Test Update Operation**:
   - Use BusinessPartner ID from previous step
   - Execute update node with CSRF token

4. **Test Delete Operation**:
   - Use BusinessPartner ID
   - Execute delete node with CSRF token

## Security Notes

- These credentials are stored encrypted in n8n
- Do not commit this file to version control
- Rotate passwords regularly
- Use S/4HANA communication users (not dialog users) for API access in production
- CSRF tokens expire after session timeout (typically 30 minutes)
- Cookies must be included with CSRF token for validation
