# Quick Reference - User Management Features

**Commit**: a492717  
**Date**: February 25, 2026

---

## 🎯 What Was Added

### 1. **Soft Delete Users** ✅
- Archive users (soft delete)
- User cannot login (403 error)
- Data preserved for audit trail
- Listable in Archived Users section
- **SUPER_ADMIN ONLY**

### 2. **Delete User Positions** ✅
- Permanently delete ALL positions
- Removes from paper_positions, paper_orders, paper_trades, ledger_entries
- Used to fix wrong backdated orders
- **IRREVERSIBLE** - Cannot undo!
- **SUPER_ADMIN ONLY**

### 3. **Archived Users List** ✅
- View all archived users
- Shows archive date and last login
- Scrollable list
- Auto-refresh button
- **SUPER_ADMIN ONLY**

---

## 📍 Where to Find These Features

**Location**: SuperAdmin Dashboard → **USER AUTH CHECK** tab

**Layout**:
```
┌─────────────────────────────────────────────┬─────────────────────────┐
│ LEFT COLUMN (Actions)                       │ RIGHT COLUMN (View)     │
├─────────────────────────────────────────────┼─────────────────────────┤
│ 1. Diagnose User Login (existing)           │ Archived Users          │
│    ↓                                        │ (list with dates)       │
│ 2. Soft Delete User (NEW)                   │                         │
│    - Input: Mobile/ID                       │ Auto-loads when you     │
│    - Button: Archive User                   │ open this tab           │
│    - Shows: Confirmation popup              │                         │
│    ↓                                        │ Shows:                  │
│ 3. Delete All Positions (NEW)               │ - Mobile/Name           │
│    - Input: Mobile/ID                       │ - Archive date          │
│    - Button: Delete ALL Positions           │ - Last login date       │
│    - Shows: Confirmation popup              │                         │
│    - Shows: Deletion summary                │ Refresh button          │
└─────────────────────────────────────────────┴─────────────────────────┘
```

---

## 🔐 Security & Permissions

- **SUPER_ADMIN users only** - Regular admins cannot use these features
- **Confirmation popups** - Must confirm before action
- **Action logging** - All operations logged in server logs
- **Archived users blocked** - Cannot login (403 error)

---

## 🚀 How to Use

### Archive a User (Safe - Data Preserved)

```
1. Go to: SuperAdmin → USER AUTH CHECK
2. Left side: "Soft Delete User (Archive)"
3. Enter: 9876543210 (mobile) or user UUID
4. Click: 🗑️ Archive User
5. Confirm: "This will ARCHIVE the user..."
✅ User appears in Archived Users list
✅ User cannot login anymore
✅ Data is safe and recoverable
```

### Delete User's Positions (Permanent - No Recovery)

```
1. Go to: SuperAdmin → USER AUTH CHECK
2. Left side: "Delete All Positions"
3. Enter: 9876543210 (mobile) or user UUID
4. Click: 🔥 Delete ALL Positions
5. Confirm: "PERMANENT! All positions will be DELETED..."
✅ All positions/orders/ledger entries deleted
✅ Shows count: "Deleted: 5 positions, 12 orders, 25 ledger entries"
❌ Cannot undo - data is permanently gone
```

### View Archived Users

```
1. Go to: SuperAdmin → USER AUTH CHECK
2. Right side: "Archived Users" (auto-loads)
3. See all archived users with dates
4. Click 🔄 Refresh to reload list
```

---

## 📊 API Endpoints

### Archive User
```bash
POST /api/v2/admin/users/{user_id}/soft-delete
Header: X-AUTH: <admin_token>
Body: (none)

Response: {
  "success": true,
  "message": "User 9876543210 has been archived",
  "user_id": "uuid",
  "user_identifier": "9876543210"
}
```

### Delete Positions
```bash
POST /api/v2/admin/users/{user_id}/positions/delete-all
Header: X-AUTH: <admin_token>
Body: (none)

Response: {
  "success": true,
  "message": "All positions deleted for user 9876543210",
  "deleted_summary": {
    "positions": 5,
    "orders": 12,
    "ledger_entries": 25,
    "total": 42
  }
}
```

### Get Archived Users
```bash
GET /api/v2/admin/users/archived
Header: X-AUTH: <admin_token>

Response: {
  "success": true,
  "count": 3,
  "archived_users": [
    {
      "user_id": "uuid",
      "mobile": "9876543210",
      "name": "John Doe",
      "archived_at": "2026-02-25T10:30:00+00:00",
      "last_login": "2026-02-20T15:45:00+00:00"
    },
    ...
  ]
}
```

---

## 🛢️ Database Schema

**New columns on `users` table**:
```sql
is_archived BOOLEAN DEFAULT FALSE  -- Mark as archived
archived_at TIMESTAMP              -- When archived
```

**Indexes added**:
```sql
idx_users_is_archived          -- For quick lookups
idx_users_archived_at          -- For sorting by archive date
```

---

## ⚠️ Important Notes

1. **Soft Delete (Archive)** = User cannot login but data readable
   - Can be recovered if needed
   - Use this for users who shouldn't access system

2. **Hard Delete (Positions)** = PERMANENT DATA LOSS
   - Removes all positions and orders
   - Use only for cleaning up wrong backdated orders
   - **Cannot undo!**

3. **Archived Users Still Show** in user lists until explicitly deleted
   - They just can't login (403 error)
   - Their data is still in database

4. **User Input** accepts:
   - Mobile number: "9876543210"
   - UUID: "550e8400-e29b-41d4-a716-446655440000"

---

## 🧪 Testing Steps

1. **Create test user** via Create Users feature
2. **Archive it** - Should appear in Archived Users list
3. **Try to login** - Should get "Account has been archived" error
4. **Create positions** for another test user
5. **Delete all positions** - Should show deletion count
6. **Check positions gone** - Dashboard should show 0 positions
7. **Verify logs** - Check server logs for action records

---

## 📋 Files Changed

1. **app/routers/admin.py** - 3 new endpoints
2. **app/routers/auth.py** - Added archived check
3. **frontend/src/pages/SuperAdmin.jsx** - New UI + handlers
4. **migrations/026_user_archival_system.sql** - Database schema

---

## 🔄 Workflow Examples

### Scenario A: User Violated Terms - Archive Them
```
User: 9876543210 violated trading rules

Step 1: Go to SuperAdmin → USER AUTH CHECK
Step 2: Soft Delete User section → Enter 9876543210
Step 3: Click Archive User → Confirm
Result: User cannot login anymore, data preserved for audit
```

### Scenario B: Wrong Historical Orders - Clean Them Up
```
User: 8888888888 placed wrong backdated orders

Step 1: Go to SuperAdmin → USER AUTH CHECK
Step 2: Delete All Positions section → Enter 8888888888
Step 3: Click Delete ALL Positions → Confirm
Step 4: See deletion report: "Deleted: 100 positions, 250 orders"
Result: All wrong orders completely removed from system
```

### Scenario C: Review Who's Been Archived
```
Question: Which users are archived?

Step 1: Go to SuperAdmin → USER AUTH CHECK
Step 2: Look at right side: Archived Users list
Step 3: See all archived users with their archive dates
Step 4: Click Refresh to reload list
Result: Complete audit trail of archived users
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Feature not showing | Verify you're SUPER_ADMIN role |
| User not found | Check mobile/UUID format |
| Already archived error | User is already archived, use Archived list to check |
| Deletion failed | Check server logs, verify user exists |
| List not loading | Click Refresh button |

---

## 📚 Related Documents

- **USER_MANAGEMENT_FEATURES.md** - Detailed technical documentation
- **FEATURE_IMPLEMENTATION_SUMMARY.md** - Summary of all features
- **IMPLEMENTATION_COMPLETE.md** - Complete implementation guide

---

**Status**: ✅ **READY FOR DEPLOYMENT**

All features implemented and committed to git (a492717).
Ready for Coolify deployment.
