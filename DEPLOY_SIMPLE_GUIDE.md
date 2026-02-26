# 🚀 HOW TO DEPLOY CHANGES - SIMPLE GUIDE

**⏱️ Time needed:** 5-10 minutes  
**Difficulty:** ⭐ Very Easy (no coding knowledge needed)

---

## What You're Doing

Your code changes are ready, but they need to be deployed to the VPS server so the website shows the new version. This guide will help you deploy it.

---

## 🎯 Easy Option: Use Python Script (Recommended ✅)

### Step 1: Open PowerShell

1. Go to **Windows Start Menu**
2. Type `PowerShell` 
3. Click **Windows PowerShell** (or **PowerShell 7** if you have it)

**You should see a window like this:**
```
PS C:\Users\YourName>
```

### Step 2: Navigate to Your Project Folder

Copy and paste this command into PowerShell:

```powershell
cd "D:\4.PROJECTS\FRESH\trading-nexus"
```

Then press **Enter**

### Step 3: Run the Deployment Script

Copy and paste this command:

```powershell
python DEPLOY_CHANGES_NOW.py
```

Then press **Enter**

### What Happens Next

The script will automatically:
1. ✅ Find your application on the VPS
2. ✅ Tell Coolify to rebuild the container
3. ✅ Wait for the rebuild to complete (2-5 minutes)
4. ✅ Tell you when it's done

**Just wait!** Don't close the window while it's running.

You should see messages like:
```
========================================================================
  FINDING YOUR APPLICATION
========================================================================

[STEP 1] Searching for your application in Coolify...
✅ Found 1 application(s)

[STEP 2] Triggering container rebuild and deployment...
✅ Deployment triggered successfully!

[STEP 3] Checking deployment status...
Status: building
Status: deployed
✅ Application is RUNNING!
```

### When It's Done ✅

When you see "✅ DEPLOYMENT COMPLETE!" - your changes are LIVE!

You can now:
1. Open http://72.62.228.112:3000 in browser (Coolify dashboard)
2. Check your app at http://72.62.228.112:8000
3. Test the watchlist changes

---

## 🖥️ Alternative Option: Use Coolify Web Dashboard

If you prefer clicking buttons instead of commands:

### Step 1: Open Coolify Dashboard

1. Open your web browser (Chrome, Edge, Firefox, etc.)
2. Go to: `http://72.62.228.112:3000`
3. Log in with your admin account

### Step 2: Find Your Application

1. Look for your application in the left sidebar or main dashboard
2. It should be named something like "backend" or "trading-nexus"

### Step 3: Deploy

1. Click on your application
2. Look for a **"Deploy"** or **"Redeploy"** button
3. Click it
4. Wait for the deployment to finish (you'll see status updates)

### Step 4: Verify

Once done, you'll see **"Running"** status in green

---

## ❌ Troubleshooting

### Problem: "Python is not recognized"

**Solution:**
- Make sure Python is installed on your computer
- Try opening a new PowerShell window
- Or use the **Coolify Dashboard option** instead

### Problem: "Connection refused" or "Cannot connect to Coolify"

**Solution:**
1. Check that the VPS is running (at `72.62.228.112`)
2. Check that Coolify is running on the VPS
3. Check API token is correct in the script

### Problem: Script runs but nothing happens

**Solution:**
1. Check the error messages in PowerShell
2. Verify your application exists in Coolify
3. Check internet connection to VPS

### Problem: Deployment takes longer than 5 minutes

**This is normal!** Container rebuilds can take 5-10 minutes depending on:
- Code size
- Dependencies to download
- VPS speed

Just wait and let it finish. Don't close PowerShell.

---

## 📋 What Changes You're Deploying

**Watchlist Tier-A Cleanup Updated:**
- ✅ Changed from 1-hour grace period to 4 PM IST daily cleanup
- ✅ Tier-A items without positions auto-remove at 4 PM
- ✅ Tier-B items stay permanently
- ✅ Items with open positions stay protected

**File Changed:**
- `app/routers/watchlist.py` (backend code)

**What the user will see:**
- Watchlist items auto-clean at predictable time (4 PM)
- No more mysterious disappearing items
- Clear behavior rules

---

## ✅ After Deployment

### Test That It Works

1. **Open your app:** http://72.62.228.112:8000
2. **Go to Watchlist tab**
3. **Add an item (before 4 PM)** → Should show with badge
4. **After 4 PM, refresh** → Tier-A item without position should disappear

### Check Logs (Optional)

If you want to see what happened:

1. Open Coolify dashboard: http://72.62.228.112:3000
2. Click your application
3. Click **"Logs"** tab
4. You should see deployment messages

---

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| Deploy changes | `python DEPLOY_CHANGES_NOW.py` |
| Check status | Go to http://72.62.228.112:3000 (Coolify) |
| View app | Go to http://72.62.228.112:8000 |
| Restart from dashboard | Click "Deploy" in Coolify UI |

---

## 📞 If You're Stuck

1. **Copy the error message** from PowerShell
2. **Check the Coolify logs** for details
3. **Wait 5 minutes and try again** (sometimes network issues)
4. **Use Coolify dashboard option** instead of the script

---

## 🎉 You Did It!

Once deployment is complete, the new watchlist cleanup logic is live and working!

**Summary:**
- ✅ Code ready? Yes ✓
- ✅ Deployment script ready? Yes ✓
- ✅ Just need to run it? Yes ✓
- ✅ No coding knowledge needed? Yes ✓

**Next:** Run `python DEPLOY_CHANGES_NOW.py` and watch it deploy! 🚀

---

**Questions?** Check the error messages in PowerShell - they usually tell you what went wrong.
