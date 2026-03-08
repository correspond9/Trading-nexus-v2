# QA BUG TRACKER - Trading Nexus Audit (UPDATED)
**Date:** March 8, 2026  
**Checkpoint:** checkpoint_testing1 (commit: 2dd5d45)  
**Testing Phases:** 2-3 COMPLETE

---

## 🔴 CRITICAL SECURITY BUGS

### BUG #1: Inadequate Role-Based Access Control  
**Severity:** 🔴 CRITICAL (Security Vulnerability)  
**Status:** **CONFIRMED - ACTIVE EXPLOIT RISK**  
**Affects:** USER, SUPER_USER roles  

**Description:**  
Regular users and super users can access highly sensitive administrative endpoints that should be restricted to ADMIN/SUPER_ADMIN only.

**Critical Security Exposures:**

#### 1. **Dhan API Credentials Exposure** (CRITICAL!)
- **Endpoint:** `GET /api/v2/admin/credentials`
- **Accessible by:** USER ✅ | SUPER_USER ✅ | ADMIN ✅ | SUPER_ADMIN ✅
- **Should be:** SUPER_ADMIN only
- **Impact:** Any user can view and potentially steal API keys, client IDs, and access tokens for the DhanHQ broker account

#### 2. **Dhan Connection Status Exposure**
- **Endpoint:** `GET /api/v2/admin/dhan/status`
- **Accessible by:** USER ✅ | SUPER_USER ✅ | ADMIN ✅ | SUPER_ADMIN ✅
- **Should be:** ADMIN+ only
- **Impact:** Users can monitor broker connection status and potentially detect vulnerabilities

#### 3. **Ledger Access Violation**
- **Endpoint:** `GET /api/v2/ledger`
- **Accessible by:** USER ✅ | SUPER_USER ✅ | ADMIN ✅ | SUPER_ADMIN ✅
- **Should be:** ADMIN+ only
- **Impact:** Users can view all ledger entries for all users, exposing financial transactions

#### 4. **Payouts Access Violation**
- **Endpoint:** `GET /api/v2/payouts`
- **Accessible by:** USER ✅ | SUPER_USER ✅ | ADMIN ✅ | SUPER_ADMIN ✅
- **Should be:** ADMIN+ only
- **Impact:** Users can view all payout records for allусers

**Reproduction Steps (Critical Credentials Leak):**
```bash
# 1. Login as regular user
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"mobile":"7777777777","password":"user123"}'

# Response contains access_token

# 2. Access admin credentials endpoint
curl http://localhost:8000/api/v2/admin/credentials \
  -H "X-AUTH: {access_token_from_step1}"

# Result: 200 OK with Dhan API credentials exposed!
```

**Expected Behavior:**
- Regular USERs should get 403 Forbidden
- SUPER_USERs should get 403 Forbidden
- Only ADMIN and SUPER_ADMIN should have access

**Root Cause:**  
Missing role-based access control decorators on sensitive endpoints in `app/routers/admin.py` and `app/routers/ledger.py`, `app/routers/payouts.py`.

**Recommended Fix:**
```python
# In app/routers/admin.py
from app.dependencies import require_super_admin, require_admin

@router.get("/credentials")
async def get_credentials(user: CurrentUser = Depends(require_super_admin)):
    # Only SUPER_ADMIN can access
    ...

@router.get("/dhan/status")
async def dhan_status(user: CurrentUser = Depends(require_admin)):
    # Only ADMIN+ can access
    ...
```

**Priority:** 🔴 **URGENT - FIX IMMEDIATELY**  
**Risk Level:** Data breach, credential theft, financial exposure

---

## 🟡 MINOR ISSUES

### ISSUE #1: Unclear SUPER_USER Role Definition
**Severity:** 🟡 LOW  
**Status:** **DOCUMENTATION NEEDED**

**Description:**  
SUPER_USER role has identical permissions to regular USER role in most areas.

**Current Access:**
| Feature | USER | SUPER_USER | Difference |
|---------|------|------------|------------|
| Trading operations | ✅ | ✅ | None |
| View own data | ✅ | ✅ | None |
| View all users | ❌ | ❌ | None |
| View admin features | ❌ | ❌ | None |

**Recommendation:**
1. Define clear purpose for SUPER_USER role
2. Implement differentiated permissions if needed
3. Or deprecate the role if not needed

---

## ✅ WORKING FEATURES

### Phase 2: Role Access Testing - ALL CORE APIS WORKING
**Status:** ✅ PASS

All core trading endpoints are functional and accessible:

#### Authentication ✅
- Login/Logout working for all roles
- Session management functional
- Auth tokens properly validated

#### Market Data ✅
- Stream status accessible
- Quote data working
- Market hours check functional

#### Trading Operations ✅
- Search instruments: ✅ Working
- View pending orders: ✅ Working
- View executed orders: ✅ Working
- View positions: ✅ Working
- View P&L summary: ✅ Working

#### Portfolio Management ✅
- Watchlist access: ✅ Working
- Margin account: ✅ Working
- Ledger access: ⚠️ Working but security issue

#### Administrative Features ✅
- User management (ADMIN+): ✅ Working
- Positions userwise (ADMIN+): ✅ Working
- Scheduler control (SUPER_ADMIN): ✅ Working
- VPS monitor (SUPER_ADMIN): ✅ Working

---

### Phase 3: Market Closed Validation - WORKING CORRECTLY
**Status:** ✅ PASS

**Test Date:** March 8, 2026 (Sunday)  
**Expected:** Market should be closed  
**Result:** ✅ PASS

**Validation Test:**
```
Attempted order placement at market closed time
Response: 403 Forbidden
Message: "Market is CLOSED. Orders can only be placed during market hours."
```

**Findings:**
✅ Order placement correctly rejected  
✅ Appropriate error message displayed  
✅ Market hours validation working as expected  
✅ Backend validation logic functioning properly

---

## UPDATED ROLE PERMISSION MATRIX

| Feature | SUPER_ADMIN | ADMIN | SUPER_USER | USER | Security Issue |
|---------|-------------|-------|------------|------|----------------|
| **Basic Features** |
| Get own profile | ✅ | ✅ | ✅ | ✅ | - |
| View stream status | ✅ | ✅ | ✅ | ✅ | - |
| View own watchlist | ✅ | ✅ | ✅ | ✅ | - |
| Search instruments | ✅ | ✅ | ✅ | ✅ | - |
| **Trading** |
| View own pending orders | ✅ | ✅ | ✅ | ✅ | - |
| View own executed orders | ✅ | ✅ | ✅ | ✅ | - |
| View own positions | ✅ | ✅ | ✅ | ✅ | - |
| View own P&L summary | ✅ | ✅ | ✅ | ✅ | - |
| View margin account | ✅ | ✅ | ✅ | ✅ | - |
| **Admin Features** |
| View ledger | ✅ | ✅ | ✅ 🔴 | ✅ 🔴 | YES - Should be ADMIN+ |
| View all users | ✅ | ✅ | ❌ | ❌ | OK |
| View payouts | ✅ | ✅ | ✅ 🔴 | ✅ 🔴 | YES - Should be ADMIN+ |
| View all user positions | ✅ | ✅ | ❌ | ❌ | OK |
| **Super Admin Features** |
| View Dhan credentials | ✅ | ✅ 🔴 | ✅ 🔴 | ✅ 🔴 | YES - Should be SUPER_ADMIN only |
| View Dhan connection | ✅ | ✅ | ✅ 🔴 | ✅ 🔴 | YES - Should be ADMIN+ |
| View schedulers | ✅ | ❌ | ❌ | ❌ | OK |
| View VPS monitor | ✅ | ❌ | ❌ | ❌ | OK |

**Legend:**  
✅ = Working as expected  
❌ = Correctly denied access  
🔴 = Security issue - should NOT have access

---

## TESTING STATUS

### Completed ✅
- [x] Phase 1: System architecture discovery
- [x] Phase 2: Role-based access testing
- [x] Phase 3: Market closed behavior validation

### In Progress 🔄
- [ ] Phase 4: Enable test mode
- [ ] Phase 5: End-to-end trading lifecycle
- [ ] Phase 6: System glitch monitoring
- [ ] Phase 7: Edge case testing
- [ ] Phase 8: Final audit report

---

## IMMEDIATE ACTION REQUIRED

### Critical Security Fix Needed:
1. **Restrict `/admin/credentials`** to SUPER_ADMIN only
2. **Restrict `/admin/dhan/status`** to ADMIN+ only
3. **Restrict `/ledger`** to ADMIN+ only
4. **Restrict `/payouts`** to ADMIN+ only

### Verification Steps After Fix:
1. Re-run role access tests
2. Verify USERs get 403 Forbidden
3. Verify ADMIN can access (except credentials)
4. Verify SUPER_ADMIN can access all

---

**Overall System Status:** 🟡 FUNCTIONAL BUT INSECURE  
**Critical Issues:** 1 (Security)  
**Recommendation:** Fix security issues before proceeding to production
