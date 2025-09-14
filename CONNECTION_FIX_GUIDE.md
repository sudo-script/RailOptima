# RailOptima Connection Issues - Diagnosis and Solutions

## Issues Identified:

### 1. ✅ API Server Status
- **Status**: WORKING CORRECTLY
- **Port**: 8000
- **Health Check**: ✅ Responding
- **CORS**: ✅ Properly configured

### 2. ❌ Frontend Issues
- **Node.js/npm**: Not installed or not in PATH
- **Frontend Server**: Not running on port 9002
- **Environment**: Missing .env.local file

### 3. ⚠️ API Data Issues
- **Trains Endpoint**: Returns empty array `[]`
- **Data Initialization**: May have issues with sample data loading

## Solutions:

### Solution 1: Install Node.js and npm
1. Download and install Node.js from https://nodejs.org/
2. Choose the LTS version (recommended)
3. Restart your terminal/PowerShell after installation
4. Verify installation:
   ```powershell
   node --version
   npm --version
   ```

### Solution 2: Create Environment Configuration
Create a file `SIHH-main/.env.local` with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

### Solution 3: Fix API Data Initialization
The trains endpoint is returning empty data. This is likely because:
- The sample data loading failed
- The data initialization in `api_stub.py` has issues

### Solution 4: Start Both Servers
1. **Start API Server** (Terminal 1):
   ```powershell
   cd "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima\support\api_support"
   python api_stub.py
   ```

2. **Start Frontend Server** (Terminal 2):
   ```powershell
   cd "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima\SIHH-main"
   npm install
   npm run dev
   ```

### Solution 5: Test Connection
After both servers are running:
1. API: http://localhost:8000/docs
2. Frontend: http://localhost:9002
3. Test API: http://localhost:8000/health

## Quick Fix Commands:

### For PowerShell (Windows):
```powershell
# Install Node.js first, then:

# Terminal 1 - API Server
cd "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima\support\api_support"
python api_stub.py

# Terminal 2 - Frontend Server  
cd "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima\SIHH-main"
npm install
npm run dev
```

### Alternative: Use the provided batch files
```powershell
# Use the existing startup script
cd "C:\Users\ASTHA CHATTERJEE\Desktop\RailOptima"
.\start-railoptima.bat
```

## Verification Steps:
1. Check API: http://localhost:8000/health
2. Check Frontend: http://localhost:9002
3. Check API Docs: http://localhost:8000/docs
4. Test trains endpoint: http://localhost:8000/trains

## Common Issues:
- **"npm not recognized"**: Install Node.js
- **"Connection Error"**: Check if API server is running
- **"Failed to fetch"**: Check CORS and API URL configuration
- **Empty data**: Check API data initialization

## Next Steps:
1. Install Node.js if not already installed
2. Create the .env.local file
3. Start both servers
4. Test the connection
