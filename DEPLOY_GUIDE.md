# Step-by-Step Guide: Deploy to GitHub & Streamlit Cloud

## Part 1: Push to GitHub

### Step 1: Initialize Git Repository

Open PowerShell in your project folder:

```powershell
cd C:\Users\vthot\N8N-DOCKER-SAP-AGENTIC-AI

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: SAP Invoice RAG system"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com
2. Click "New repository" (green button)
3. Repository name: `sap-invoice-rag`
4. Description: "AI-powered SAP invoice query system"
5. **Keep it Private** (contains sensitive code)
6. **DON'T** check "Initialize with README" (we already have files)
7. Click "Create repository"

### Step 3: Push to GitHub

```powershell
# Add remote repository (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/sap-invoice-rag.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note:** You'll be prompted for GitHub credentials. Use a Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when pushing

---

## Part 2: Deploy to Streamlit Cloud

### Step 1: Prepare for Deployment

**Important Files Checklist:**
- ✅ `streamlit_app_cloud.py` (created - uses direct imports instead of API)
- ✅ `requirements.txt` (core dependencies)
- ✅ `requirements_api.txt` (additional deps)
- ✅ `.gitignore` (excludes .env file)
- ✅ `README.md` (project documentation)

### Step 2: Create Streamlit Cloud Account

1. Go to https://share.streamlit.io
2. Click "Sign up" or "Continue with GitHub"
3. Authorize Streamlit to access your GitHub

### Step 3: Deploy New App

1. Click "New app" button
2. Configure deployment:
   - **Repository:** `YOUR_USERNAME/sap-invoice-rag`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app_cloud.py` ⚠️ (NOT streamlit_app.py)
   - **App URL:** Choose custom URL like `sap-invoice-assistant`

### Step 4: Add Secrets (CRITICAL)

1. Click "Advanced settings" before deploying
2. Go to "Secrets" section
3. Add your API keys in TOML format:

```toml
# .streamlit/secrets.toml format
OPENAI_API_KEY = "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"
PINECONE_API_KEY = "pcsk_3Uzock_S27SseQXqSSjys7E3P8EjpwXV23EwCiyJHDZWbphGPxxGZjbXB9N1ucjx4VEiTU"
```

4. Click "Save"

### Step 5: Deploy!

1. Click "Deploy!" button
2. Wait 2-5 minutes for deployment
3. Streamlit will:
   - Clone your repository
   - Install dependencies from requirements.txt
   - Run streamlit_app_cloud.py

### Step 6: Access Your App

Your app will be available at:
```
https://YOUR_APP_NAME.streamlit.app
```

For example: `https://sap-invoice-assistant.streamlit.app`

---

## Part 3: Update Deployed App

### When you make changes:

```powershell
# Make your code changes

# Commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push origin main
```

**Streamlit Cloud will automatically redeploy** when it detects changes!

---

## Part 4: Configure Secrets in Code

Update `streamlit_app_cloud.py` to use Streamlit secrets:

Already done! The `sap_invoice_rag.py` loads from `.env` locally and Streamlit automatically makes secrets available as environment variables.

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:** Add missing packages to `requirements.txt`:

```powershell
# Test locally first
pip freeze > requirements_full.txt

# Copy needed packages to requirements.txt
```

Then push to GitHub.

### Issue: "API key not found"

**Solution:** Check Streamlit Cloud secrets:
1. Go to app settings
2. Click "Secrets" in sidebar
3. Verify TOML format is correct
4. Restart app

### Issue: App is slow

**Solution:** Streamlit Cloud free tier has limitations:
- 1 GB RAM
- 1 CPU core
- Consider caching results:

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_invoice_count():
    return get_invoice_count()
```

### Issue: Can't connect to Pinecone

**Solution:** Verify:
1. Pinecone API key is correct in secrets
2. Index name matches: `n8n-s4hana-new`
3. Namespace matches: `invoice-documents`

---

## File Structure for Deployment

```
sap-invoice-rag/
├── .gitignore                  ✅ Excludes .env
├── README.md                   ✅ Documentation
├── requirements.txt            ✅ Core dependencies
├── requirements_api.txt        ✅ Extra dependencies
├── sap_invoice_rag.py         ✅ Main RAG system
├── streamlit_app_cloud.py     ✅ Cloud version (no API)
├── streamlit_app.py           ⚠️ Local version (uses API)
├── api_server.py              ⚠️ Not needed for cloud
├── sap_invoice_indexer.py     ⚠️ Optional
└── .env                       🚫 NOT in GitHub (gitignored)
```

---

## Quick Commands Summary

```powershell
# 1. Initialize and push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/sap-invoice-rag.git
git branch -M main
git push -u origin main

# 2. Update after changes
git add .
git commit -m "Updated feature X"
git push origin main
```

---

## Cost Considerations

### Streamlit Cloud (Free Tier)
- ✅ FREE hosting
- ✅ 1 private app
- ✅ Unlimited public apps
- ✅ Auto-deployment from GitHub
- ❌ 1GB RAM limit
- ❌ App sleeps after inactivity

### OpenAI API Costs
- Embeddings: ~$0.0001 per query
- GPT-4o-mini: ~$0.0015 per query
- Estimated: **$0.002 per query**

### Pinecone Costs
- Starter Plan: **FREE** up to 1 index
- 100K vectors included
- Your 32 invoices: **FREE**

**Total monthly cost: $0-5** (depending on usage)

---

## Alternative: Deploy Both API + Streamlit

If you want to keep the API architecture:

1. **Deploy API to Railway:**
   - Connect GitHub repo
   - Set `api_server.py` as entry point
   - Add environment variables
   - Get public URL

2. **Update Streamlit app:**
   ```python
   # In streamlit_app.py
   API_URL = "https://your-api.railway.app"
   ```

3. **Deploy Streamlit normally**

This allows API to be used by multiple clients (n8n, mobile app, etc.)

---

You're ready to deploy! 🚀
