@echo off
REM Financial Metrics Analyzer - Windows Startup Script
REM This script sets up and runs both backend and frontend servers

echo 🚀 Starting Financial Metrics Analyzer...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.10+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd audit-ui
npm install
if errorlevel 1 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
)

cd ..

echo ✅ Dependencies installed successfully

REM Start backend server
echo 🔧 Starting backend server...
start "Backend Server" cmd /k "python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo 🎨 Starting frontend server...
cd audit-ui
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo 🎉 Financial Metrics Analyzer is now running!
echo.
echo 📊 Frontend: http://localhost:3000
echo 🔧 Backend API: http://127.0.0.1:8000
echo 📚 API Docs: http://127.0.0.1:8000/docs
echo.
echo Two command windows have opened - one for backend and one for frontend.
echo Close both windows to stop the servers.
echo.
pause
