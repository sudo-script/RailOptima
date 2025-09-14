# 🚀 RailOptima - Easy Start Guide

## 🎯 **Super Easy Way to Start Everything**

### **Option 1: Double-Click to Start (Recommended)**
1. **Double-click** `start-railoptima.bat` file
2. **Wait** for both servers to start (about 10-15 seconds)
3. **Open Chrome** and go to: **http://localhost:9002**

### **Option 2: PowerShell Script**
1. **Right-click** on `start-railoptima.ps1`
2. **Select** "Run with PowerShell"
3. **Open Chrome** and go to: **http://localhost:9002**

## 🌐 **Access Your Application**

- **Frontend (Main App)**: http://localhost:9002
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 **What the Scripts Do**

1. **Start Backend**: Runs your `api_stub.py` on port 8000
2. **Start Frontend**: Runs Next.js on port 9002
3. **Open Windows**: Creates separate windows for each server
4. **Show URLs**: Displays all the important links

## 🛑 **How to Stop**

- **Close the terminal windows** that opened
- Or press **Ctrl+C** in each terminal window

## 🆘 **If Something Goes Wrong**

1. **Check if ports are free**: Make sure nothing else is using ports 8000 or 9002
2. **Restart**: Close all terminals and run the script again
3. **Check Python**: Make sure Python is installed and in PATH
4. **Check Node.js**: Make sure Node.js and npm are installed

## 📁 **File Structure**
```
RailOptima/
├── start-railoptima.bat     ← Double-click this!
├── start-railoptima.ps1     ← PowerShell version
├── support/api_support/
│   └── api_stub.py          ← Your backend API
└── SIHH-main/
    ├── package.json         ← Frontend dependencies
    └── src/                 ← Frontend code
```

## 🎉 **That's It!**

Just double-click `start-railoptima.bat` and you're ready to go!
