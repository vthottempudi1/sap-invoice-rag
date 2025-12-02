# AI Agent for S/4HANA Sales Data

## Overview
Chat with an AI agent to fetch and analyze S/4HANA sales order data. Just ask in natural language!

**Examples:**
- "Show me all sales orders"
- "Get orders for customer 25100080"
- "What's the total value of all orders?"
- "Find sales order number 1"
- "Show me orders from sales org 2510 and save to Google Sheets"

---

## Prerequisites

### You Need:
1. **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **n8n Cloud Account** - Already set up at vthottempudi1.app.n8n.cloud
3. **S/4HANA Credentials** - Already configured (s4gui4/Sap@123456)
4. **Google Sheets** (optional) - For saving data

---

## Part 1: Get OpenAI API Key

### Step 1.1: Create OpenAI Account

1. Go to [OpenAI Platform](https://platform.openai.com/signup)
2. Sign up with email or Google account
3. Verify your email

### Step 1.2: Get API Key

1. Go to [API Keys](https://platform.openai.com/api-keys)
2. Click **"+ Create new secret key"**
3. Name it: `n8n-s4hana-agent`
4. Click **Create secret key**
5. **COPY THE KEY** immediately (you won't see it again!)
   - Format: `sk-proj-...` or `sk-...`

### Step 1.3: Add Credits (if needed)

- New accounts may get free credits
- Or add payment method: Settings → Billing → Add payment method
- Minimum: $5 (will last for thousands of queries)

---

## Part 2: Setup in n8n Cloud

### Step 2.1: Add OpenAI Credential

1. Go to https://vthottempudi1.app.n8n.cloud
2. Click profile icon → **Credentials**
3. Click **+ Add Credential**
4. Search for: **OpenAI**
5. Fill in:
   ```
   Credential Name: OpenAI API
   API Key: sk-proj-your-key-here
   ```
6. Click **Save**

### Step 2.2: Import AI Agent Workflow

1. Click **Workflows** → **+ Add Workflow**
2. Click **⋮ menu** → **Import from File**
3. Select: `n8n-ai-agent-s4hana.json`
4. Click **Import**

### Step 2.3: Configure Workflow Nodes

The workflow will automatically use your credentials, but verify:

#### Node: "Fetch from S/4HANA"
- Credential: **S/4HANA Basic Auth** (should already be selected)

#### Node: "AI Agent" and "OpenAI Chat Model"
- Credential: **OpenAI API** (select the one you just created)

#### Node: "Save to Google Sheets" (optional)
- Credential: **Google Sheets OAuth** (if you want to save data)
- Document: Select your **S/4HANA Sales Orders** spreadsheet
- Sheet: **Sheet1**

---

## Part 3: Activate and Test

### Step 3.1: Activate the Workflow

1. Click the **Active** toggle switch (top-right)
2. Status should turn green
3. Workflow is now listening for chat messages

### Step 3.2: Open the Chat

1. Click the **Chat** button (top-right, speech bubble icon)
2. A chat panel will open on the right side

### Step 3.3: Start Chatting!

Try these example queries:

**Basic Queries:**
```
Show me all sales orders
```

**Filtered Queries:**
```
Get sales orders for customer 25100080
```

```
Show me sales order number 1
```

```
Find orders from sales organization 2510
```

**Analysis Queries:**
```
What's the total value of all orders?
```

```
How many orders do we have?
```

```
Which customers have placed orders?
```

**Save to Google Sheets:**
```
Get all sales orders and save to Google Sheets
```

```
Show me customer 25100080 orders and save them
```

---

## Part 4: How It Works

### Workflow Architecture

```
┌──────────────────────┐
│ You: "Show me all    │
│ sales orders"        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│ AI Agent (GPT-4o-mini)           │
│ - Understands your question      │
│ - Decides what to fetch          │
│ - Calls S/4HANA Query Tool       │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ S/4HANA Query Tool               │
│ - Builds OData filter            │
│ - Fetches from S/4HANA           │
│ - Returns formatted data         │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ AI Agent Response                │
│ "I found 5 sales orders:         │
│ - Order 1: €400.00               │
│ - Order 2: €400.00               │
│ - Order 3: €10.00                │
│ Total value: €810.00"            │
└──────────┬───────────────────────┘
           │
           ▼ (if you asked to save)
┌──────────────────────────────────┐
│ Google Sheets                    │
│ Data automatically saved         │
└──────────────────────────────────┘
```

### What the AI Can Do

✅ **Understand natural language** - No need for exact commands
✅ **Filter data** - By customer, order number, sales org, etc.
✅ **Calculate totals** - Sum amounts, count orders
✅ **Format results** - Present data in readable format
✅ **Save to Google Sheets** - When you ask
✅ **Ask clarifying questions** - If your request is unclear

---

## Part 5: Advanced Queries

### Complex Filters

The AI can translate your requests to OData filters:

**Request:** "Show me orders over €100"
**AI builds:** `$filter=TotalNetAmount gt 100`

**Request:** "Get orders from October 2023"
**AI builds:** `$filter=SalesOrderDate ge datetime'2023-10-01' and SalesOrderDate lt datetime'2023-11-01'`

**Request:** "Find orders with billing block"
**AI builds:** `$filter=HeaderBillingBlockReason ne ''`

### Multi-Step Analysis

```
You: Show me all orders
AI: [Returns 15 orders]

You: What's the average order value?
AI: The average order value is €86.67

You: Which customer has the most orders?
AI: Customer 25100080 has 2 orders

You: Save all the data to Google Sheets
AI: I've saved 15 sales orders to your Google Sheet
```

---

## Part 6: Customization

### Change AI Model

In the **"OpenAI Chat Model"** node, you can change:

**For faster/cheaper responses:**
- Model: `gpt-3.5-turbo`
- Temperature: `0.3`

**For smarter responses:**
- Model: `gpt-4o` (more expensive)
- Temperature: `0.3`

### Customize AI Instructions

In the **"AI Agent"** node, edit the prompt to change behavior:

```javascript
You are an AI assistant for S/4HANA sales analysis.

Your personality: Professional and concise

Special instructions:
- Always show currency symbols
- Format large numbers with commas
- Highlight any orders with billing blocks
- Suggest saving to Google Sheets after showing data
```

### Add More Tools

You can add additional tools for the AI:

**Calculator Tool** - For complex math
**HTTP Request Tool** - Fetch from other systems
**Database Tool** - Query other databases
**Email Tool** - Send reports via email

---

## Part 7: Cost Estimation

### OpenAI Costs (as of 2024)

**GPT-4o-mini** (Recommended):
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Average query: ~$0.001 (1/10th of a cent)
- **100 queries ≈ $0.10**

**GPT-3.5-turbo** (Cheaper):
- Input: $0.50 per 1M tokens
- Output: $1.50 per 1M tokens
- Average query: ~$0.002
- **100 queries ≈ $0.20**

**GPT-4o** (Smartest):
- Input: $5.00 per 1M tokens
- Output: $15.00 per 1M tokens
- Average query: ~$0.02
- **100 queries ≈ $2.00**

---

## Part 8: Troubleshooting

### Error: "OpenAI API key invalid"

**Solution:**
1. Check API key is correct (starts with `sk-`)
2. Verify you copied the full key
3. Check OpenAI account has credits

### Error: "Tool returned no results"

**Cause:** S/4HANA filter found no matches

**Solution:**
- Try broader query: "Show me all orders"
- Check if data exists in S/4HANA
- Verify filter criteria

### AI gives generic responses

**Cause:** Not using the S/4HANA tool

**Solution:**
1. Check tool is connected to AI Agent
2. Verify S/4HANA credentials are valid
3. Make your query more specific: "Get sales orders from S/4HANA"

### Chat button not visible

**Cause:** Workflow not activated

**Solution:**
1. Click **Active** toggle (must be green)
2. Refresh the page
3. Look for chat bubble icon in top-right

---

## Example Conversations

### Example 1: Basic Query

**You:** Show me all sales orders

**AI:** I found 15 sales orders in the system:

1. Order 1 - Customer 25100080 - €400.00 EUR
2. Order 2 - Customer 25100080 - €400.00 EUR
3. Order 3 - Customer 25100273 - €10.00 EUR
4. Order 4 - Customer 25100273 - €100.00 EUR
5. Order 5 - Customer 25100273 - €60.00 EUR
[... more orders ...]

Total value: €970.00 EUR

Would you like me to save these to Google Sheets?

---

### Example 2: Filtered Search

**You:** Get me orders for customer 25100080

**AI:** I found 2 orders for customer 25100080:

1. **Order 1**
   - Date: 2023-10-09
   - Amount: €400.00 EUR
   - PO: test
   - Status: A (Active)

2. **Order 2**
   - Date: 2023-10-09
   - Amount: €400.00 EUR
   - PO: 1993
   - Status: A (Active)

Total: €800.00 EUR

---

### Example 3: Analysis

**You:** What's the total value of all orders and how many customers do we have?

**AI:** Based on the sales order data:

📊 **Summary:**
- **Total Orders:** 15
- **Total Value:** €970.00 EUR
- **Unique Customers:** 2
  - Customer 25100080 (2 orders)
  - Customer 25100273 (13 orders)

**Average Order Value:** €64.67 EUR

---

## Summary Checklist

- [ ] OpenAI API key obtained
- [ ] OpenAI credential added to n8n Cloud
- [ ] AI Agent workflow imported
- [ ] S/4HANA credential configured
- [ ] Workflow activated (green toggle)
- [ ] Chat panel opened
- [ ] Test query successful
- [ ] Google Sheets configured (optional)

---

## Benefits of AI Agent Approach

✅ **Natural Language** - No need to learn OData syntax
✅ **Conversational** - Ask follow-up questions
✅ **Smart Filtering** - AI understands your intent
✅ **Data Analysis** - Calculate totals, averages, etc.
✅ **Flexible** - Combine queries and actions
✅ **User-Friendly** - Anyone can use it, no training needed
✅ **Extensible** - Add more data sources easily

---

## Next Steps

1. **Import the workflow** and add OpenAI credential
2. **Activate it** and open the chat
3. **Start asking questions!**
4. **Share the chat link** with your team (n8n Pro feature)

You now have an AI assistant that can answer questions about your S/4HANA sales data! 🤖
