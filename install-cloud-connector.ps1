# Cloud Connector Installation Script
param(
    [string]$ZipPath = "$env:USERPROFILE\Downloads\sapcc-2.17.1-windows-x64.zip",
    [string]$InstallDir = "C:\SAP\CloudConnector"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SAP Cloud Connector Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if zip file exists
Write-Host "Step 1: Checking for downloaded file..." -ForegroundColor Yellow
if (Test-Path $ZipPath) {
    Write-Host "[OK] Found: $ZipPath" -ForegroundColor Green
} else {
    Write-Host "[ERROR] File not found: $ZipPath" -ForegroundColor Red
    Write-Host "`nPlease download Cloud Connector from:" -ForegroundColor Yellow
    Write-Host "https://tools.hana.ondemand.com/#cloud" -ForegroundColor White
    Write-Host "`nSave it to: $env:USERPROFILE\Downloads\" -ForegroundColor White
    exit 1
}

# Create installation directory
Write-Host "`nStep 2: Creating installation directory..." -ForegroundColor Yellow
if (!(Test-Path $InstallDir)) {
    New-Item -Path $InstallDir -ItemType Directory -Force | Out-Null
    Write-Host "[OK] Created: $InstallDir" -ForegroundColor Green
} else {
    Write-Host "[OK] Directory exists: $InstallDir" -ForegroundColor Green
}

# Extract files
Write-Host "`nStep 3: Extracting Cloud Connector..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $ZipPath -DestinationPath $InstallDir -Force
    Write-Host "[OK] Extraction complete" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Extraction failed: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host "`nStep 4: Verifying installation..." -ForegroundColor Yellow
$goBat = Join-Path $InstallDir "go.bat"
if (Test-Path $goBat) {
    Write-Host "[OK] go.bat found" -ForegroundColor Green
} else {
    Write-Host "[ERROR] go.bat not found" -ForegroundColor Red
    exit 1
}

# Start Cloud Connector
Write-Host "`nStep 5: Starting Cloud Connector..." -ForegroundColor Yellow
Write-Host "Starting service (this may take 30-60 seconds)..." -ForegroundColor White

Set-Location $InstallDir
Start-Process -FilePath "cmd.exe" -ArgumentList "/c go.bat" -WindowStyle Normal

Write-Host "[OK] Cloud Connector starting..." -ForegroundColor Green
Write-Host "`nWaiting for service to initialize" -NoNewline -ForegroundColor White

# Wait for service to start
for ($i = 1; $i -le 12; $i++) {
    Start-Sleep -Seconds 5
    Write-Host "." -NoNewline
    $port = Get-NetTCPConnection -LocalPort 8443 -ErrorAction SilentlyContinue
    if ($port) {
        Write-Host "`n[OK] Cloud Connector is running on port 8443" -ForegroundColor Green
        $serviceRunning = $true
        break
    }
}

if (!$serviceRunning) {
    Write-Host "`n[WARNING] Cloud Connector may still be starting..." -ForegroundColor Yellow
    Write-Host "Please wait a moment then access https://localhost:8443" -ForegroundColor White
}

# Display next steps
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Admin UI: https://localhost:8443" -ForegroundColor White
Write-Host "`nDefault Login:" -ForegroundColor Yellow
Write-Host "  Username: Administrator" -ForegroundColor White
Write-Host "  Password: manage" -ForegroundColor White
Write-Host "`n[!] Change password on first login`n" -ForegroundColor Yellow

Write-Host "Configuration Steps:" -ForegroundColor Yellow
Write-Host "1. Open https://localhost:8443" -ForegroundColor White
Write-Host "2. Login and change password" -ForegroundColor White
Write-Host "3. Add BTP Subaccount:" -ForegroundColor White
Write-Host "   Region: cf.us10.hana.ondemand.com" -ForegroundColor Gray
Write-Host "   Subaccount: d57623dbtrial" -ForegroundColor Gray
Write-Host "   User: vthottempudi1@gmail.com" -ForegroundColor Gray
Write-Host "4. Add S/4HANA System:" -ForegroundColor White
Write-Host "   Internal: s4hana2020.support.com:8009" -ForegroundColor Gray
Write-Host "   Virtual: s4hana-virtual.internal:8009" -ForegroundColor Gray
Write-Host "5. See CLOUD-CONNECTOR-SETUP.md for details`n" -ForegroundColor White

Write-Host "Opening browser..." -ForegroundColor White
Start-Sleep -Seconds 3
Start-Process "https://localhost:8443"

Write-Host "`n[SUCCESS] Setup completed!`n" -ForegroundColor Green
