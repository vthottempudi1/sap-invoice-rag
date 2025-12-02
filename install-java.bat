@echo off
echo ========================================
echo Cloud Connector - Java Installation
echo ========================================
echo.

echo SAP Cloud Connector requires Java 11 or later
echo.

echo Step 1: Download Java
echo.
echo Please download Java from ONE of these options:
echo.
echo Option A: Amazon Corretto 11 (Recommended - Free)
echo https://corretto.aws/downloads/latest/amazon-corretto-11-x64-windows-jdk.msi
echo.
echo Option B: Oracle JDK 11
echo https://www.oracle.com/java/technologies/downloads/#java11-windows
echo.
echo Option C: Adoptium Eclipse Temurin 11
echo https://adoptium.net/temurin/releases/?version=11
echo.
pause

echo.
echo Step 2: Install Java
echo.
echo Run the downloaded MSI installer
echo Accept all defaults
echo.
pause

echo.
echo Step 3: Verify Java Installation
echo.
java -version
if errorlevel 1 (
    echo [ERROR] Java not found in PATH
    echo.
    echo Please add Java to your PATH:
    echo 1. Open System Properties ^> Environment Variables
    echo 2. Add Java bin directory to PATH
    echo    Example: C:\Program Files\Amazon Corretto\jdk11.x.x_x\bin
    echo.
) else (
    echo [SUCCESS] Java installed successfully!
    echo.
)

echo.
echo Step 4: Install Cloud Connector
echo.
echo Now run: install-cloud-connector-with-java.bat
echo.
pause
