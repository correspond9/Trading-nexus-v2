# 🚀 DEPLOY WATCHLIST CHANGES - POWERSHELL VERSION

**For Windows PowerShell Users**

---

## ✅ CORRECT COMMAND FOR POWERSHELL

Copy and paste this:

```powershell
cd "D:\4.PROJECTS\FRESH\trading-nexus"; python DEPLOY_CHANGES_NOW.py
```

**Note:** Use `;` (semicolon) not `&&` in PowerShell!

---

## 🎯 ALTERNATIVE: Run In Two Steps

If the above doesn't work, run these one at a time:

### Step 1:
```powershell
cd "D:\4.PROJECTS\FRESH\trading-nexus"
```

Press Enter

### Step 2:
```powershell
python DEPLOY_CHANGES_NOW.py
```

Press Enter

---

## ⏱️ WHAT HAPPENS NEXT

The script will:
1. Connect to VPS
2. Find your application
3. Trigger rebuild
4. Monitor status (5-10 minutes)
5. Confirm when done ✅

Just wait and watch the progress!

---

## ✅ SUCCESS LOOKS LIKE

You'll see:
```
========================================================================
  FINDING YOUR APPLICATION
========================================================================

[STEP 1] Searching for your application in Coolify...
✅ Found 1 application(s)

[STEP 2] Triggering container rebuild and deployment...
✅ Deployment triggered successfully!

[STEP 3] Checking deployment status...
✅ Application is RUNNING!

========================================================================
  DEPLOYMENT COMPLETE ✨
========================================================================
```

Then your changes are LIVE at http://72.62.228.112:8000

---

## 🆘 IF "python" COMMAND DOESN'T WORK

Try these alternatives:

```powershell
python3 DEPLOY_CHANGES_NOW.py
```

Or:

```powershell
py DEPLOY_CHANGES_NOW.py
```

Or verify Python is installed:

```powershell
python --version
```

Should show: Python 3.x.x

---

**QUICK COMMAND (Copy This):**

```powershell
cd "D:\4.PROJECTS\FRESH\trading-nexus"; python DEPLOY_CHANGES_NOW.py
```

That's all you need! 🚀
