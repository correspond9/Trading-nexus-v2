# QA BUG TRACKER - Trading Nexus Audit
**Date:** March 8, 2026  
**Checkpoint:** checkpoint_testing1 (commit: 2dd5d45)  
**Testing Phase:** 2 - Role Access Testing

---

## 🔴 CRITICAL BUGS

### BUG #1: Core Trading Endpoints Return 404
**Severity:** CRITICAL  
**Status:** **BROKEN - SYSTEM UNUSABLE**  
**Affects:** ALL user roles  

**Description:**  
Multiple core trading endpoints are returning 404 Not Found errors, making the trading system completely non-functional.

**Affected Endpoints:**
- `GET /api/v2/market-data/stream-status` - Returns 404
- `GET /api/v2/search/instruments/search` - Returns 404
- `GET /api/v2/orders` - Returns 404
- `GET /api/v2/orders/executed` - Returns 404
- `GET /api/v2/positions` - Returns 404
- `GET /api/v2/positions/pnl/summary` - Returns 404

**Impact:**  
Users cannot:
- View market stream status  
- Search for trading instruments
- View their pending orders
- View their executed orders
- View their open positions
- View their P&L summary

**Reproduction Steps:**
1. Login as any user (Super Admin, Admin, Super User, or User)
2. Make GET request to `/api/v2/orders`
3. Observe 404 error

**Expected Behavior:**  
These endpoints should return appropriate data or empty arrays/objects when no data exists.

**Root Cause (Suspected):**  
Likely route registration issue in FastAPI or missing route handlers in the routers.

**Recommended Fix:**
1. Verify router imports in `app/main.py`
2. Check that all routers are properly included with correct prefix
3. Verify endpoint decorators in router files match the expected paths
4. Check if there's a prefix mismatch (e.g., extra `/api` in route definition)

---

## 🟠 HIGH PRIORITY BUGS

### BUG #2: Inadequate Role-Based Access Control
**Severity:** HIGH (Security Issue)  
**Status:** **SECURITY VULNERABILITY**  
**Affects:** User, Super User roles  

**Description:**  
Regular USERs and SUPER_USERs can access sensitive admin-only endpoints that should be restricted.

**Security Issues Identified:**

1. **Regular USER can access:**
   - `GET /admin/credentials` → 200 OK (Can view Dhan API credentials!)
   - `GET /admin/dhan/status` → 200 OK
   - `GET /ledger` → 200 OK
   - `GET /payouts` → 200 OK

2. **SUPER_USER can access:**
   - `GET /admin/credentials` → 200 OK (Can view Dhan API credentials!)
   - `GET /admin/dhan/status` → 200 OK
   - `GET /ledger` → 200 OK
   - `GET /payouts` → 200 OK

**Expected Behavior:**
- `/admin/credentials` should ONLY be accessible by SUPER_ADMIN
- `/admin/dhan/status` should be ADMIN+ only
- `/ledger` should be ADMIN+ only
- `/payouts` should be ADMIN+ only

**Impact:**  
Potential data breach - regular users can view:
- DhanHQ API credentials (client ID, API keys)
- All user ledger entries
- All payout information
- Dhan connection status

**Reproduction Steps:**
1. Login as User (mobile: 7777777777)
2. Make GET request to `/api/v2/admin/credentials`
3. Observe 200 OK response with credential data

**Root Cause:**  
Missing or incomplete role-based access control decorators on admin endpoints.

**Recommended Fix:**
1. Review all admin endpoints in `app/routers/admin.py`
2. Ensure proper role check dependencies like `Depends(require_admin)` or `Depends(require_super_admin)` are applied
3. Audit all sensitive endpoints for proper authentication
4. Add unit tests for role-based access control

---

## 🟡 MEDIUM PRIORITY BUGS

### BUG #3: Admin Cannot Access Super Admin Features
**Severity:** MEDIUM  
**Status:** **PERMISSION ISSUE**  
**Affects:** ADMIN role  

**Description:**  
ADMIN users are blocked from accessing certain features that might be appropriate for admins:
- `GET /admin/schedulers` → 403 Forbidden
- `GET /admin/vps-monitor/status` → 403 Forbidden

**Analysis:**  
These might be intentionally restricted to SUPER_ADMIN only, but should be documented clearly.

**Recommendation:**
1. Document the exact role hierarchy and permissions
2. Consider if ADMIN should have read-only access to schedulers and VPS monitor
3. Update UI to hide inaccessible features based on role

---

### BUG #4: Super User Has Same Admin Access as User
**Severity:** MEDIUM  
**Status:** **ROLE DEFINITION UNCLEAR**  
**Affects:** SUPER_USER role  

**Description:**  
The SUPER_USER role appears to have the same access level as a regular USER. The purpose and privileges of SUPER_USER are unclear.

**Access Comparison:**
| Feature | USER | SUPER_USER |
|---------|------|------------|
| Get own profile | ✅ | ✅ |
| View own watchlist | ✅ | ✅ |
| View margin account | ✅ | ✅ |
| View ledger (BUG) | ✅ | ✅ |
| View payouts (BUG) | ✅ | ✅ |
| View admin credentials (BUG) | ✅ | ✅ |
| View all users | ❌ | ❌ |
| View schedulers | ❌ | ❌ |

**Recommendation:**
1. Define clear purpose of SUPER_USER role
2. Implement differentiated permissions
3. Document role hierarchy in system documentation

---

## 🟢 WORKING FEATURES

### Authentication ✅
- Login system working for all roles
- Session management functional
- `/auth/me` endpoint working correctly

### Accessible Features by Super Admin:
- ✅ Get own profile
- ✅ View own watchlist
- ✅ View margin account
- ✅ View ledger
- ✅ View all users
- ✅ View payouts
- ✅ View all user positions
- ✅ View Dhan credentials
- ✅ View Dhan connection status
- ✅ View schedulers
- ✅ View VPS monitor

---

## ROLE PERMISSION MATRIX (ACTUAL)

| Feature | SUPER_ADMIN | ADMIN | SUPER_USER | USER |
|---------|-------------|-------|------------|------|
| Get own profile | ✅ | ✅ | ✅ | ✅ |
| View stream status | ❌ (404) | ❌ (404) | ❌ (404) | ❌ (404) |
| View own watchlist | ✅ | ✅ | ✅ | ✅ |
| Search instruments | ❌ (404) | ❌ (404) | ❌ (404) | ❌ (404) |
| View own pending orders | ❌ (404) | ❌ (404) | ❌ (404) | ❌ (404) |
| View own executed orders | ❌ (404) | ❌ (404) | ❌ (404) | ❌ (404) |
| View own positions | ❌ (404) | ❌ (404) | ❌ (404) | ❌ (404) |
| View own P&L summary | ❌ (404) | ❌ (404) | ❌ (404) | ❌ (404) |
| View margin account | ✅ | ✅ | ✅ | ✅ |
| View ledger | ✅ | ✅ | ✅ 🔴 | ✅ 🔴 |
| View all users | ✅ | ✅ | ❌ | ❌ |
| View payouts | ✅ | ✅ | ✅ 🔴 | ✅ 🔴 |
| View all user positions | ✅ | ✅ | ❌ | ❌ |
| View Dhan credentials | ✅ | ✅ | ✅ 🔴 | ✅ 🔴 |
| View Dhan connection status | ✅ | ✅ | ✅ 🔴 | ✅ 🔴 |
| View schedulers | ✅ | ❌ | ❌ | ❌ |
| View VPS monitor | ✅ | ❌ | ❌ | ❌ |

**Legend:**  
✅ = Working as expected  
❌ (404) = Route not found / broken endpoint  
❌ = Access denied (403)  
🔴 = Security issue - should NOT have access

---

## NEXT STEPS

### Immediate Actions Required:
1. **FIX BUG #1** - Restore core trading endpoints (orders, positions, search, market-data)
2. **FIX BUG #2** - Implement proper role-based access control for admin endpoints
3. **VERIFY** - Re-test all endpoints after fixes

### Testing Continuation:
- [ ] Phase 3: Market closed behavior validation
- [ ] Phase 4: Enable test mode
- [ ] Phase 5: End-to-end trading flow testing
- [ ] Phase 6: System glitch detection
- [ ] Phase 7: Edge case testing
- [ ] Phase 8: Final audit report

---

**Test Status:** Phase 2 COMPLETE  
**System Status:** 🔴 CRITICAL BUGS - Trading functionality broken  
**Security Status:** 🔴 HIGH RISK - Role-based access control inadequate
