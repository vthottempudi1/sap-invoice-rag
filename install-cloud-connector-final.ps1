# Complete Cloud Connector Installation (After Java is installed)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Cloud Connector Installation" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Verify Java
Write-Host "Step 1: Verifying Java installation..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Java installed: $javaVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Java not found!" -ForegroundColor Red
    Write-Host "Please install Java first:install-java.bat" -ForegroundColor White
    exit 1
}

# Step 2: Install Cloud Connector
Write-Host "`nStep 2: Installing Cloud Connector..." -ForegroundColor Yellow
$msiPath = "$env:USERPROFILE\Downloads\sapcc-2.18.2-windows-x64.msi"

if (!(Test-Path $msiPath)) {
    Write-Host "[ERROR] Cloud Connector MSI not found at: $msiPath" -ForegroundColor Red
    exit 1
}

Write-Host "Installing from: $msiPath" -ForegroundColor Gray
Start-Process msiexec.exe -ArgumentList "/i `"$msiPath`" /qn INSTALLDIR=`"C:\SAP\CloudConnector`"" -Wait -NoNewWindow
Write-Host "[OK] Installation completed" -ForegroundColor Green

# Step 3: Find installation directory
Write-Host "`nStep 3: Locating Cloud Connector..." -ForegroundColor Yellow
$ccPaths = @("C:\SAP\CloudConnector", "C:\SAP\scc20", "C:\Program Files\SAP\scc20")
$ccPath = $null

foreach ($path in $ccPaths) {
    if (Test-Path $path) {
        $ccPath = $path
        Write-Host "[OK] Found at: $ccPath" -ForegroundColor Green
        break
    }
}

if (!$ccPath) {
    Write-Host "[ERROR] Cloud Connector not found in expected locations" -ForegroundColor Red
    Write-Host "Searching..." -ForegroundColor Yellow
    
    Get-ChildItem "C:\" -Directory -Recurse -Depth 3 -ErrorAction SilentlyContinue | 
        Where-Object { $_.Name -match "scc|CloudConnector" } |
        ForEach-Object { Write-Host "Found: $($_.FullName)" -ForegroundColor Gray }
    exit 1
}

# Step 4: Start Cloud Connector
Write-Host "`nStep 4: Starting Cloud Connector..." -ForegroundColor Yellow
Set-Location $ccPath

if (Test-Path ".\go.bat") {
    Write-Host "Executing go.bat..." -ForegroundColor Gray
    Start-Process cmd.exe -ArgumentList "/c go.bat" -WindowStyle Normal
    
    Write-Host "Waiting for service to start" -NoNewline -ForegroundColor White
    for ($i = 1; $i -le 15; $i++) {
        Start-Sleep -Seconds 4
        Write-Host "." -NoNewline
        $test = Test-NetConnection localhost -Port 8443 -WarningAction SilentlyContinue
        if ($test.TcpTestSucceeded) {
            Write-Host "`n[SUCCESS] Cloud Connector is running!" -ForegroundColor Green
            break
        }
    }
} else {
    Write-Host "[ERROR] go.bat not found in $ccPath" -ForegroundColor Red
    exit 1
}

# Step 5: Open Admin UI
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Admin UI: https://localhost:8443" -ForegroundColor White
Write-Host "`nDefault Login:" -ForegroundColor Yellow
Write-Host "  Username: Administrator" -ForegroundColor White
Write-Host "  Password: manage" -ForegroundColor White
Write-Host "`n[!] Change password on first login`n" -ForegroundColor Yellow

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure BTP Subaccount connection" -ForegroundColor White
Write-Host "2. Add S/4HANA system mapping" -ForegroundColor White
Write-Host "3. Create BTP Destination" -ForegroundColor White
Write-Host "`nSee: CLOUD-CONNECTOR-SETUP.md for detailed configuration`n" -ForegroundColor Gray

Write-Host "Opening browser..." -ForegroundColor White
Start-Sleep -Seconds 3
Start-Process "https://localhost:8443"

Write-Host "[SUCCESS] Setup completed!`n" -ForegroundColor Green
