# 🚀 DEPLOYMENT OPTIONS - CHOOSE YOUR METHOD

**Date:** February 26, 2026  
**What:** Deploy watchlist changes to VPS  
**Time:** 5-10 minutes  
**Difficulty:** ⭐ Easy (No coding needed)

---

## 📋 What's Being Deployed?

**File Changed:** `app/routers/watchlist.py`

**What Changed:**
- Tier-A cleanup from 1-hour grace period → 4 PM IST daily cleanup
- Tier-A items without positions auto-remove at 4 PM
- More predictable behavior

**Files to Deploy:**
- ✅ `app/routers/watchlist.py` - Main change
- ✅ `app/` - Entire backend (auto-deployed)
- ✅ `frontend/` - Frontend assets (auto-deployed)

---

## 🎯 OPTION 1: One-Click API Deployment (Easiest ✅)

**Best for:** Everyone - simplest and safest

### Step 1: Open PowerShell

1. Press **Windows Key + R**
2. Type `powershell`
3. Press **Enter**

### Step 2: Navigate to Project

Copy and paste:
```powershell
cd "D:\4.PROJECTS\FRESH\trading-nexus"
```

Press **Enter**

### Step 3: Run Deployment

Copy and paste:
```powershell
python DEPLOY_CHANGES_NOW.py
```

Press **Enter**

### What Happens

The script will:
1. ✅ Connect to your VPS via API
2. ✅ Find your application
3. ✅ Tell Coolify to rebuild container
4. ✅ Monitor the deployment (takes 2-5 min)
5. ✅ Confirm when it's done

**You'll see:**
```
========================================================================
  FINDING YOUR APPLICATION
========================================================================

[STEP 1] Searching for your application in Coolify...
✅ Found 1 application(s)
  📦 backend
     UUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
     Status: running

[STEP 2] Triggering container rebuild and deployment...
✅ Deployment triggered successfully!

[STEP 3] Checking deployment status...
Status: deploying
Status: running
✅ Application is RUNNING!

[STEP 4] Next Steps
📱 Your application should now be accessible at:
   🔗 http://72.62.228.112:8000
========================================================================
  DEPLOYMENT COMPLETE ✨
========================================================================
```

### ✅ Then What?

When you see "✅ DEPLOYMENT COMPLETE", open:
- **http://72.62.228.112:8000** - Your app
- Test watchlist to verify changes work

---

## 🖥️ OPTION 2: Use Coolify Dashboard (Click Buttons)

**Best for:** If you prefer using UI instead of commands

### Step 1: Open Coolify

1. Open web browser (Chrome, Edge, Firefox)
2. Go to: **http://72.62.228.112:3000**
3. Log in with your admin account

### Step 2: Find Application

1. Look in left sidebar for your application
2. Usually named: `backend` or `trading-nexus`
3. Click on it

### Step 3: Deploy

1. You'll see a green **"Deploy"** or **"Redeploy"** button
2. Click it
3. Wait for status to turn green (says "Running")

Takes 2-5 minutes. You can watch the progress in the logs.

### ✅ When Done

You'll see:
- Application status: **Running** (green)
- Last deploy: timestamp will update

---

## 🔌 OPTION 3: SSH Direct Connection (Advanced)

**Best for:** If Coolify API isn't working

### Prerequisites

You need:
- SSH access to VPS (IP: `72.62.228.112`)
- SSH client on Windows (Windows 10/11 built-in, or PuTTY)
- VPS credentials

### Using Windows Built-In SSH

**Step 1: Open PowerShell**

```powershell
ssh root@72.62.228.112
```

Press **Enter**

Enter your VPS password when prompted

**Step 2: Run Deployment Commands**

Once logged in, copy and paste these commands one by one:

```bash
# Stop current container
cd /root/Trading-Nexus
docker-compose down

# Get latest code
git pull origin main

# Build new image (takes 2-5 minutes)
docker-compose build

# Start new container
docker-compose up -d

# Check status
docker-compose ps
```

**Step 3: Verify**

Should see "running" status for your containers.

Then access: **http://72.62.228.112:8000**

---

## ⚡ OPTION 4: Using Existing Deploy Scripts

You have several ready-made scripts. Try in PowerShell:

### Using Python Deployment Script

```powershell
cd "D:\4.PROJECTS\FRESH\trading-nexus"
python deploy_via_coolify_api.py
```

### Using PowerShell Script

```powershell
cd "D:\4.PROJECTS\FRESH\trading-nexus"
.\coolify_deploy.ps1
```

### Using Shell Script (if you're on WSL)

```bash
cd /mnt/d/4.PROJECTS/FRESH/trading-nexus
bash deploy.sh
```

---

## 🎯 RECOMMENDED FLOW

### Try in This Order:

1. **Start with Option 1** (DEPLOY_CHANGES_NOW.py)
   - Simplest, most reliable
   - Just run `python DEPLOY_CHANGES_NOW.py`

2. **If Option 1 fails**, try Option 2 (Coolify Dashboard)
   - Manual clicking works if API is down
   - Just click "Deploy" button

3. **If Option 2 fails**, try Option 3 (SSH)
   - Direct command access to VPS
   - More control, more technical

4. **If all fail**, check:
   - Is VPS running?
   - Is Coolify running?
   - Is internet connection working?

---

## ✅ VERIFICATION CHECKLIST

After deployment, check:

- [ ] No errors in PowerShell
- [ ] Coolify shows "Running" status
- [ ] Can open http://72.62.228.112:8000
- [ ] Can open http://72.62.228.112:3000 (Coolify)
- [ ] App loaded without errors

### Test Watchlist Changes

1. Open app at http://72.62.228.112:8000
2. Go to Watchlist tab
3. Add an instrument (before 4 PM)
4. Should show [Tier-A] or [Tier-B] badge
5. After 4 PM, if you refresh without position, item should disappear

---

## ❌ TROUBLESHOOTING

### "Python is not recognized"

**Solution:**
- Make sure Python is installed
- Or use Option 2 (click buttons in Coolify)

### "Cannot connect to Coolify"

**Solution:**
- Verify VPS IP is correct: `72.62.228.112`
- Verify VPS is running
- Check network/internet connection

### "Deployment takes forever"

**Normal!** Docker builds take 5-10 minutes.
- Just wait
- Don't close PowerShell
- Check Coolify logs for progress

### "Application status is stuck on 'deploying'"

**Solution:**
1. Wait another 5 minutes
2. Go to Coolify dashboard
3. Check "Logs" tab for error messages
4. Or restart container manually via SSH

### "Changes still not showing on UI"

**Try:**
1. **Clear browser cache:** Ctrl+Shift+Delete
2. **Hard reload:** Ctrl+Shift+R
3. **Wait 1 minute:** Sometimes takes time to propagate
4. **Check different URL:** Try incognito window

### "Getting API token errors"

**Check:**
- API token in script is correct
- API token has correct permissions
- Coolify is running on VPS

---

## 📊 DEPLOYMENT STATUS

**Your VPS:**
- IP: `72.62.228.112`
- Coolify: http://72.62.228.112:3000
- App: http://72.62.228.112:8000
- API Token: Valid ✅

**Your Code:**
- Changes: Ready ✅
- Tested: ✅
- Ready to deploy: ✅

**All systems green! Just deploy.** 🟢

---

## ⏭️ WHAT TO DO NOW

### Quick Start (30 seconds):

1. Open PowerShell
2. Type: `cd "D:\4.PROJECTS\FRESH\trading-nexus"`
3. Type: `python DEPLOY_CHANGES_NOW.py`
4. Press Enter
5. Wait for "✅ DEPLOYMENT COMPLETE"

### Result:

In 5-10 minutes, your changes will be LIVE! 🚀

---

## 📞 HELP

If anything goes wrong:

1. **Read the error message** - Usually tells you what's wrong
2. **Check Coolify logs** - http://72.62.228.112:3000 → Logs tab
3. **Try a different option** - Api fails? Use Dashboard instead
4. **Wait and retry** - Network issues are temporary

---

## 🎉 SUMMARY

| Method | Easiest? | Fastest? | When to Use |
|--------|----------|----------|------------|
| Option 1 (API) | ✅ YES | ✅ YES | **TRY FIRST** |
| Option 2 (Dashboard) | ✅ YES | ⭐ Slow | If Option 1 fails |
| Option 3 (SSH) | ❌ More steps | ✅ YES | Direct control |
| Option 4 (Scripts) | ⭐ Sometimes | ✅ YES | Advanced |

**Recommendation:** Start with Option 1. It's the simplest.

---

**Ready to deploy? Run this:**

```powershell
python DEPLOY_CHANGES_NOW.py
```

**That's it! Your changes will be live in 5-10 minutes.** ✨

---

**Problems? See TROUBLESHOOTING section above.**
