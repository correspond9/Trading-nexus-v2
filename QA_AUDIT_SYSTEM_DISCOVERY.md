# TRADING NEXUS - SYSTEM ARCHITECTURE DISCOVERY
**QA Audit Report - Phase 1**  
**Date:** March 8, 2026  
**Checkpoint:** checkpoint_testing1 (commit: 2dd5d45)  
**Status:** System Running & Healthy

---

## 1. DOCKER SERVICES ARCHITECTURE

### Container Overview
| Service | Container Name | Image | Port | Health Status |
|---------|---------------|-------|------|---------------|
| Database | trading_nexus_db | postgres:16-alpine | 127.0.0.1:5432 | ✅ Healthy |
| Backend | trading_nexus_backend | trading-nexus-backend | 0.0.0.0:8000 | ✅ Healthy |
| Frontend | trading_nexus_frontend | trading-nexus-frontend | 0.0.0.0:80 | ✅ Running |
| Mock Dhan | trading_nexus_mockdhan | trading-nexus-mockdhan | 0.0.0.0:9000 | ✅ Healthy |

### Service Dependencies
```
frontend (Nginx)
  ├─→ backend:8000 (/api/* proxy)
  └─→ Serves React SPA on port 80

backend (FastAPI)
  ├─→ db:5432 (PostgreSQL)
  └─→ mockdhan:9000 (Market Data)

mockdhan (Mock Trading Engine)
  └─→ Simulates DhanHQ API & WebSocket feeds

db (PostgreSQL 16)
  └─→ Persistent volume: trading_nexus_pg_data
```

---

## 2. BACKEND API ARCHITECTURE

### API Routes by Module

#### 🔐 Authentication (`/v2/auth`)
- `POST /login` - User authentication
- `POST /logout` - User session termination
- `GET /me` - Current user details
- `POST /portal/signup` - Portal user registration
- `GET /portal/users` - List portal users

#### 👤 User Management (`/v2/admin/users`)
- `GET /users` - List all users
- `GET /users/{user_id}` - User details
- `POST /users` - Create new user
- `PATCH /users/{user_id}` - Update user
- `POST /users/{user_id}/funds` - Add/withdraw funds
- `POST /users/{user_id}/soft-delete` - Archive user
- `GET /users/archived` - List archived users

#### 📊 Market Data (`/v2/market-data`)
- `GET /underlying-ltp/{symbol}` - Get LTP for symbol
- `GET /quote` - Get quote data
- `GET /snapshot/{token}` - Token snapshot
- `GET /stream-status` - WebSocket stream status
- `GET /etf-tierb-status` - ETF Tier-B status
- `POST /stream-reconnect` - Reconnect streams

#### 🔍 Search (`/v2/search`)
- `GET /subscriptions/search` - Search subscriptions
- `GET /instruments/search` - Search instruments
- `GET /instruments/futures/search` - Search futures
- `GET /options/strikes/search` - Search option strikes

#### 📈 Option Chain (`/v2/option-chain`)
- `GET /live` - Live option chain
- `GET /available/expiries` - Available expiry dates
- `WS /ws/live` - WebSocket live option chain

#### 📋 Watchlist (`/v2/watchlist`)
- `GET /{user_id}` - Get user watchlist
- `POST /add` - Add to watchlist
- `POST /remove` - Remove from watchlist

#### 🛒 Orders (`/v2/orders`)
- `POST /` - Place new order
- `GET /` - Get pending orders
- `GET /executed` - Get executed orders
- `GET /historic/orders` - Historic orders
- `GET /{order_id}` - Order details
- `DELETE /{order_id}` - Cancel order

#### 📦 Positions (`/v2/positions`)
- `GET /` - Get open positions
- `GET /equity-holdings` - Equity holdings
- `POST /{position_id}/close` - Close position
- `GET /pnl/summary` - PnL summary
- `GET /pnl/historic` - Historic PnL

#### 🧺 Baskets (`/v2/baskets`)
- `GET /` - List baskets
- `POST /` - Create basket
- `POST /execute` - Execute basket
- `DELETE /{basket_id}` - Delete basket
- `POST /{basket_id}/legs` - Add legs to basket
- `POST /{basket_id}/margin` - Calculate basket margin

#### 💰 Margin (`/v2/margin`)
- `POST /calculate` - Calculate margin requirement
- `GET /account` - Account margin details
- `GET /span-data` - SPAN margin data
- `POST /nse-refresh` - Refresh NSE margin data

#### 📖 Ledger (`/v2/ledger`)
- `GET /` - Get ledger entries

#### 💸 Payouts (`/v2/payouts`)
- `GET /` - List payouts
- `POST /` - Create payout
- `PATCH /{payout_id}` - Update payout status

#### 🔌 WebSocket Feed (`/v2/ws-feed`)
- `WS /prices` - Price updates feed
- `WS /feed` - General market feed

#### ⚙️ Super Admin (`/v2/admin`)
**Credentials & Auth:**
- `POST /credentials/rotate` - Rotate credentials
- `GET /credentials` - Get credentials
- `GET /credentials/active` - Active credentials
- `POST /credentials/save` - Save new credentials
- `GET /auth-mode` - Get auth mode
- `POST /auth-mode` - Set auth mode
- `POST /auth-mode/switch` - Switch auth mode
- `POST /auth-mode/reattempt` - Retry authentication
- `GET /auth-status` - Authentication status

**Token & Streams:**
- `GET /token/status` - Token status
- `POST /token/refresh` - Refresh token
- `GET /ws/status` - WebSocket status
- `GET /subscriptions` - Active subscriptions
- `POST /mode` - Set mode
- `GET /mode` - Get mode

**Dhan Integration:**
- `GET /dhan/status` - Dhan connection status
- `POST /dhan/connect` - Connect to Dhan
- `POST /dhan/disconnect` - Disconnect from Dhan
- `GET /dhan/subscriptions` - Dhan subscriptions

**Instruments:**
- `POST /scrip-master/refresh` - Refresh scrip master
- `GET /scrip-master/status` - Scrip master status
- `POST /reload-scrip-master` - Reload scrip master

**Subscription Lists:**
- `GET /subscription-lists/{list_name}` - Get subscription list
- `GET /subscription-lists/{list_name}/symbols` - List symbols
- `POST /subscription-lists/{list_name}` - Update subscription list

**Market Config:**
- `GET /market-config` - Get market configuration
- `POST /market-config` - Update market configuration

**Position Management:**
- `GET /positions/userwise` - All user positions
- `GET /users/{user_id}/positions` - User-specific positions
- `POST /users/{user_id}/positions/delete-all` - Delete all user positions
- `POST /users/{user_id}/positions/delete-specific` - Delete specific positions
- `POST /backdate-position` - Backdate position
- `POST /force-exit` - Force exit position

**Brokerage Plans:**
- `GET /brokerage-plans` - List brokerage plans
- `POST /brokerage-plans` - Create brokerage plan
- `PUT /brokerage-plans/{plan_id}` - Update plan
- `DELETE /brokerage-plans/{plan_id}` - Delete plan
- `POST /users/{user_id}/brokerage-plans` - Assign plan to user

**Schedulers:**
- `GET /schedulers` - List all schedulers
- `POST /schedulers/{name}/{action}` - Control scheduler

**Charges:**
- `GET /charge-calculation/status` - Charge calculation status
- `POST /charge-calculation/run` - Run charge calculation
- `POST /charge-calculation/recompute-historic` - Recompute historic charges

**Option Chain:**
- `POST /option-chain/recalibrate-atm` - Recalibrate ATM strikes
- `POST /option-chain/rebuild-skeleton` - Rebuild option chain

**Misc Admin:**
- `GET /rate-limits` - Get rate limits
- `POST /greeks/interval` - Set Greeks polling interval
- `POST /close-price/rollover` - Trigger close price rollover
- `POST /subscriptions/rollover` - Rollover subscriptions
- `POST /upload-nse-files` - Upload NSE margin files
- `POST /diagnose-login` - Diagnose login issues
- `GET /vps-monitor/status` - VPS monitor status
- `GET /vps-monitor/samples` - VPS monitor samples
- `POST /vps-monitor/start` - Start VPS monitoring
- `POST /vps-monitor/stop` - Stop VPS monitoring
- `GET /notifications` - Get admin notifications
- `POST /logo/upload` - Upload logo
- `GET /logo` - Get logo
- `DELETE /logo` - Delete logo

---

## 3. FRONTEND PAGES & ROUTES

### Public Routes
- `/login` - Login page

### Protected Routes (Authenticated)
- `/` → redirects to `/trade`
- `/trade` - Main trading terminal
- `/profile` - User profile
- `/portfolio` - Portfolio view

### Admin/Super Admin Routes
- `/trade/all-positions` - All MIS positions (Admin+)
- `/all-positions-normal` - All normal positions (Admin+)
- `/all-positions-userwise` - Positions by user (Admin+)
- `/pandl` - P&L reports (Admin+)
- `/users` - User management (Admin+)
- `/payouts` - Payout management (Admin+)
- `/ledger` - Ledger view (Admin+)
- `/trade-history` - Historic orders (Admin+)
- `/dashboard` - Super Admin dashboard (Super Admin only)

### Portal Routes (learn.domain)
- `/` - Landing page
- `/crash-course` - Trading education
- `/signup` - User signup

---

## 4. FRONTEND COMPONENTS STRUCTURE

### Core Components
- `Layout` - Main application layout
- `ErrorBoundary` - Error handling wrapper
- `ProtectedRoute` - Route authentication guard

### Trading Components
Located in `/frontend/src/pages`:
- `BASKETS.jsx` - Basket trading interface
- `OPTIONS.jsx` - Options trading
- `STRADDLE.jsx` - Straddle strategies
- `WATCHLIST.jsx` - Market watchlist
- `OrderBook.tsx` - Order book display
- `Orders.jsx` - Order management
- `POSITIONS.jsx` - Position tracking
- `PositionsMIS.jsx` - MIS positions view
- `PositionsNormal.jsx` - Normal positions view
- `PositionsUserwise.jsx` - User-wise positions
- `Portfolio.jsx` - Portfolio overview
- `PandL.jsx` - Profit & Loss
- `TradeHistory.jsx` - Historical trades
- `HistoricOrders.jsx` - Historic orders

### Admin Components
- `Users.jsx` - User management
- `Payouts.jsx` - Payout management
- `Ledger.jsx` - Ledger interface
- `SuperAdmin.jsx` - Super admin dashboard
- `Profile.jsx` - User profile

---

## 5. DATABASE SCHEMA

### Core Tables (from migrations)
- `instrument_master` - All trading instruments
- `users` - User accounts & authentication
- `positions` - Open positions tracking
- `orders` - Order management
- `trades` - Executed trades
- `ledger` - Financial ledger entries
- `payouts` - Payout records
- `baskets` - Basket orders
- `subscription_lists` - Market data subscriptions
- `watchlist` - User watchlists
- `brokerage_plans` - Brokerage plan definitions
- `margin_data` - SPAN margin data cache
- `exchange_holidays` - Trading holidays

---

## 6. KEY FEATURES IDENTIFIED

### Trading Features
1. **Order Placement**
   - Market orders
   - Limit orders
   - Order modification
   - Order cancellation

2. **Position Management**
   - Real-time position tracking
   - Position closing
   - MIS auto-squareoff
   - Force exit capability

3. **Market Data**
   - Live price feeds (WebSocket)
   - Option chains
   - Market depth (20 levels)
   - Greeks calculation
   - Close price tracking

4. **Advanced Trading**
   - Basket orders
   - Super orders (Target/SL/Trailing)
   - Options strategies (Straddles)
   - Futures trading

5. **Portfolio Management**
   - Equity holdings
   - P&L tracking (real-time & historic)
   - Ledger management
   - Margin calculation

6. **User Management**
   - Multi-tier roles (User, Super User, Admin, Super Admin)
   - Fund management
   - Brokerage plans
   - User archiving

### System Features
1. **Authentication**
   - Login/logout
   - Session management
   - Role-based access control
   - Portal signup

2. **Market Hours**
   - Market open/close detection
   - Exchange holiday management
   - After-market handling

3. **Background Services**
   - Token auto-refresh (TOTP)
   - WebSocket stream management
   - Greeks polling
   - Close price rollover
   - Charge calculation
   - MIS auto-squareoff scheduler
   - Watchlist cleanup

4. **Admin Controls**
   - Dhan connection management
   - Stream control
   - Scrip master refresh
   - Margin data refresh
   - Scheduler control
   - VPS monitoring

---

## 7. TECHNOLOGY STACK

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL 16
- **WebSocket:** Native FastAPI WebSocket
- **Market Data:** DhanHQ API (or Mock)
- **Background Tasks:** APScheduler
- **Authentication:** JWT-based sessions

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **Routing:** React Router v6
- **UI:** TailwindCSS
- **State:** React Context API
- **HTTP:** Axios
- **WebSocket:** Native WebSocket API

### Infrastructure
- **Containerization:** Docker Compose
- **Reverse Proxy:** Nginx
- **Database:** PostgreSQL with persistent volume

---

## 8. NEXT STEPS - TESTING PLAN

### Phase 2: User Role Testing
✅ Test credentials provided:
- Super Admin: 9999999999 / admin123
- Admin: 8888888888 / admin123
- User: 7777777777 / user123
- Super User: 6666666666 / super123

### Phase 3: Market Closed Validation
- Verify rejection of orders when market is closed
- Confirm error messages
- Test backend validation logic

### Phase 4: Enable Test Mode
- Configure system for simulated market open
- Bypass market hours restrictions for testing

### Phase 5-7: Trading Lifecycle & Glitch Detection
- End-to-end order flow testing
- Real-time updates validation
- Error handling verification
- Edge case testing

---

**Discovery Status:** ✅ COMPLETE  
**Ready for Testing:** YES  
**System Health:** ALL GREEN
