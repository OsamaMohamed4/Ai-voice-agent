# Complete Setup Guide

Follow these steps to get your Voice Agent up and running.

##  Quick Start Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] LiveKit account created
- [ ] Gemini API key obtained
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Agent running
- [ ] Frontend running

---

## Step-by-Step Instructions

### Step 1: Get LiveKit Credentials

1. **Go to LiveKit Cloud**
   ```
   https://cloud.livekit.io/
   ```

2. **Sign up for free account**
   - Click "Sign Up"
   - Use your email or GitHub account
   - No credit card required for free tier

3. **Create a new project**
   - Click "Create Project"
   - Give it a name (e.g., "Voice Agent")
   - Click "Create"

4. **Get your credentials**
   - Go to "Settings" → "Keys"
   - You'll see:
     - **WebSocket URL** (looks like: `wss://your-project.livekit.cloud`)
     - **API Key** (starts with `API`)
     - **API Secret** (long string)
   - Copy these - you'll need them soon!

### Step 2: Get Gemini API Key (3 minutes)

1. **Go to Google AI Studio**
   ```
   https://makersuite.google.com/app/apikey
   ```

2. **Sign in with Google account**

3. **Create API Key**
   - Click "Create API Key"
   - Select "Create API key in new project" or use existing
   - Copy the key (starts with `AI`)

4. **Important**: This is FREE tier with generous limits:
   - 60 requests per minute
   - 1,500 requests per day
   - Perfect for development!

### Step 3: Clone and Setup Backend

```bash
# Clone the repository
git clone 
cd voice-agent-livekit

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Backend Environment

1. **Create `.env` file in `backend/` directory**

2. **Add your credentials:**
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxxxxx
   LIVEKIT_API_SECRET=your_secret_here
   GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxx
   ```

3. **Replace with your actual values** from Steps 1 and 2

### Step 6: Setup Frontend

```bash
# Open new terminal
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Step 7: Configure Frontend Environment

1. **Create `.env` file in `frontend/` directory**

2. **Add the same LiveKit credentials:**
   ```env
   REACT_APP_LIVEKIT_URL=wss://your-project.livekit.cloud
   REACT_APP_LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxxxxx
   REACT_APP_LIVEKIT_API_SECRET=your_secret_here
   ```

### Step 8: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python realtime_gemini_agent.py dev
```
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Browser should automatically open at `http://localhost:3000`
