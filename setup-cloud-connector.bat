@echo off
echo ========================================
echo SAP Cloud Connector Setup Script
echo ========================================
echo.

echo Step 1: Downloading Cloud Connector...
echo Please download manually from:
echo https://tools.hana.ondemand.com/#cloud
echo.
echo Look for: "Cloud Connector" section
echo Download: "Windows" version (sapcc-X.X.X-windows-x64.zip)
echo Save to: %USERPROFILE%\Downloads\
echo.
pause

echo.
echo Step 2: Creating installation directory...
set INSTALL_DIR=C:\SAP\CloudConnector
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo Created: %INSTALL_DIR%
) else (
    echo Directory already exists: %INSTALL_DIR%
)

echo.
echo Step 3: Extracting Cloud Connector...
echo Please extract the downloaded sapcc-*.zip file to:
echo %INSTALL_DIR%\
echo.
pause

echo.
echo Step 4: Starting Cloud Connector...
echo Changing directory to %INSTALL_DIR%
cd /d "%INSTALL_DIR%"

if exist "go.bat" (
    echo Starting Cloud Connector...
    start "" "%INSTALL_DIR%\go.bat"
    echo.
    echo Cloud Connector is starting...
    echo Wait 30 seconds, then access the admin UI at:
    echo https://localhost:8443
    echo.
    echo Default credentials:
    echo Username: Administrator
    echo Password: manage
    echo.
) else (
    echo ERROR: go.bat not found!
    echo Please ensure you extracted the files to %INSTALL_DIR%
    echo.
)

echo.
echo Step 5: Opening Cloud Connector UI...
timeout /t 30 /nobreak
start https://localhost:8443

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Login to Cloud Connector at https://localhost:8443
echo 2. Configure BTP Subaccount connection
echo 3. Add S/4HANA system access
echo.
echo See: BTP-DESTINATION-SETUP.md for detailed configuration
echo.
pause
