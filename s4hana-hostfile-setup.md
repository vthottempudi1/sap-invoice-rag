# S/4HANA Host File Configuration

## Purpose
Map the S/4HANA system hostname to its IP address for local access.

## Host Entry Details
- **IP Address**: `49.206.196.74`
- **Hostname**: `s4hana2020.support.com`

## Windows Configuration Steps

### Method 1: Using Notepad as Administrator (Recommended)

1. Click **Start** menu
2. Type **Notepad**
3. Right-click on **Notepad** → Select **Run as administrator**
4. Click **File** → **Open**
5. Navigate to: `C:\Windows\System32\drivers\etc`
6. Change file filter from "Text Documents (*.txt)" to **All Files (*.*)**
7. Open the **hosts** file
8. Scroll to the bottom and add this line:
   ```
   49.206.196.74    s4hana2020.support.com
   ```
9. Click **File** → **Save**
10. Close Notepad

### Method 2: Desktop Copy Method

1. Click **Start** menu → Type **Run** (or press `Win + R`)
2. Type: `drivers` and press Enter (this opens `C:\Windows\System32\drivers`)
3. Navigate to the **etc** folder
4. **Copy** the `hosts` file to your **Desktop**
5. Right-click the `hosts` file on Desktop → Open with **Notepad**
6. Add this line at the end:
   ```
   49.206.196.74    s4hana2020.support.com
   ```
7. **Save** the file and close Notepad
8. **Copy** the modified `hosts` file from Desktop
9. Navigate back to `C:\Windows\System32\drivers\etc`
10. **Paste** the file (you'll be prompted for administrator permission)
11. Click **Yes** to replace the existing file

### Method 3: PowerShell Command (Quick)

Run PowerShell as Administrator and execute:

```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n49.206.196.74    s4hana2020.support.com"
```

## Verification

After adding the host entry, verify it works:

### Using PowerShell:
```powershell
# Check if entry exists
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "s4hana2020"

# Test DNS resolution
ping s4hana2020.support.com

# Test connection
Test-NetConnection s4hana2020.support.com -Port 443
```

### Expected Results:
- Ping should resolve to `49.206.196.74`
- Test-NetConnection should show connection attempt to the correct IP

## Update n8n Workflow URLs

After configuring the host file, update all S/4HANA URLs in your n8n workflows:

**Before:**
```
https://your-s4hana-system.com/sap/opu/odata/sap/API_BUSINESS_PARTNER/...
```

**After:**
```
https://s4hana2020.support.com/sap/opu/odata/sap/API_BUSINESS_PARTNER/...
```

### Common S/4HANA OData Endpoints:

```
# Business Partner API
https://s4hana2020.support.com/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner

# Sales Order API
https://s4hana2020.support.com/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder

# Material API
https://s4hana2020.support.com/sap/opu/odata/sap/API_PRODUCT_SRV/A_Product

# Customer API
https://s4hana2020.support.com/sap/opu/odata/sap/API_CUSTOMER_SRV/A_Customer
```

## Troubleshooting

### Issue: "Access Denied" when saving hosts file
**Solution**: Make sure you're running Notepad or PowerShell as Administrator

### Issue: Changes not taking effect
**Solution**: 
1. Flush DNS cache:
   ```powershell
   ipconfig /flushdns
   ```
2. Restart your browser or n8n container

### Issue: Ping works but HTTPS doesn't connect
**Solution**: 
- Check if S/4HANA system is accessible on port 443 (HTTPS)
- Verify firewall settings
- Check if VPN is required for access

## Security Notes

- The hosts file overrides DNS resolution
- Only add trusted IP addresses
- Document all custom host entries
- Backup the original hosts file before modifications
- Remove entries when no longer needed

## Backup Current Hosts File

Before making changes, create a backup:

```powershell
Copy-Item C:\Windows\System32\drivers\etc\hosts C:\Windows\System32\drivers\etc\hosts.backup
```

To restore:
```powershell
Copy-Item C:\Windows\System32\drivers\etc\hosts.backup C:\Windows\System32\drivers\etc\hosts
```
