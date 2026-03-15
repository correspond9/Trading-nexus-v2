# Trading Nexus Mobile App — Separate Repository Setup

The Android mobile app (`frontend/android/`) is **not part of this repository**.
It lives — or will live — in its own standalone repository.

---

## Why separate?

- Independent git history and release cycle for the mobile app
- Separate issue tracking, CI/CD, and deployment pipeline
- Keeps this (backend + web frontend) repository focused and lean
- Avoids committing Gradle build artifacts or generated Capacitor files here

---

## Repository layout decision

| Codebase | Repository |
|---|---|
| FastAPI backend + React web frontend | **this repo** (`Trading-nexus-v2`) |
| Android native app (Capacitor wrapper) | **new repo** (e.g. `trading-nexus-android`) |

---

## What stays in this repo

| File / Folder | Purpose |
|---|---|
| `frontend/src/` | React source — shared logic for both web and mobile |
| `frontend/capacitor.config.ts` | Capacitor app config (appId, appName, webDir) |
| `frontend/package.json` | Includes `@capacitor/*` dependencies needed to regenerate the Android project |

The `frontend/android/` folder is listed in `.gitignore` so it will never be committed here again.

---

## Setting up the new Android repository

### 1 — Create the new repository on GitHub

Create a new (empty) repository, for example `trading-nexus-android`.

### 2 — Copy the existing Android project files

> **Note for new developers:** If you have just cloned `Trading-nexus-v2` you will not have a `frontend/android/` folder — skip straight to step 4 to regenerate it first, then come back here.

The `frontend/android/` folder should already exist on your local machine from a previous `npx cap add android` run. Copy it out:

```bash
cp -r /path/to/Trading-nexus-v2/frontend/android /path/to/Trading-nexus-android
cd /path/to/Trading-nexus-android
```

### 3 — Initialise git and push

```bash
git init
git add .
git commit -m "chore: initial Android Capacitor project"
git remote add origin git@github.com:<your-org>/trading-nexus-android.git
git push -u origin main
```

### 4 — Regenerate from scratch (alternative)

If you prefer a clean start, regenerate the Android project from this repo:

```bash
# In the Trading-nexus-v2 frontend directory
cd frontend
npm install
npm run build          # produces dist/ (the web bundle)
npx cap add android    # creates a fresh frontend/android/ folder
npx cap sync android   # copies web bundle into the native project
```

Then copy the freshly generated `frontend/android/` folder into the new repo as described in step 2, and follow the git initialisation instructions in step 3.

---

## Keeping the two repos in sync

The Android app wraps the compiled web bundle. Whenever the web frontend changes:

1. In `Trading-nexus-v2/frontend/`:
   ```bash
   npm run build
   npx cap sync android
   ```
2. Copy updated `frontend/android/app/src/main/assets/public/` into the mobile repo, or automate this with a CI step.

---

## Shared configuration

Both repos share the same Capacitor app identity:

| Setting | Value |
|---|---|
| `appId` | `com.tradingnexus.app` |
| `appName` | `Trading Nexus` |
| `webDir` | `dist` |

This is defined in `frontend/capacitor.config.ts` (this repo). Keep it in sync with the Android project in the separate repo.

---

## Recommended separate-repo structure

```
Trading-nexus-android/
├── app/
│   ├── build.gradle
│   ├── capacitor.build.gradle
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml
│           ├── java/com/tradingnexus/app/MainActivity.java
│           ├── assets/public/     ← compiled web bundle goes here
│           └── res/
├── build.gradle
├── capacitor.settings.gradle
├── gradle/
├── gradle.properties
├── gradlew
├── gradlew.bat
├── settings.gradle
├── variables.gradle
└── README.md                      ← add your own mobile-specific docs here
```
