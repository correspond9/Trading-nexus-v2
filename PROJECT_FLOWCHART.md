# Trading Nexus - Complete Project Flowchart

## 🎯 Project Overview

**Trading Nexus** is a comprehensive trading platform with statutory charge calculation capabilities, built with FastAPI backend and React frontend, deployed via Docker containers.

---

## 📊 System Architecture Flowchart

```mermaid
graph TB
    %% External Services
    subgraph "External Services"
        DHAN[DhanHQ API]
        NSE[NSE Data Feed]
        BSE[BSE Data Feed]
        MCX[MCX Data Feed]
    end

    %% Frontend Layer
    subgraph "Frontend Layer"
        UI[React SPA]
        NGINX[Nginx Reverse Proxy]
    end

    %% Backend Layer
    subgraph "Backend Layer"
        API[FastAPI Application]
        AUTH[Authentication Service]
        WS[WebSocket Manager]
        SCHED[Background Schedulers]
    end

    %% Business Logic Layer
    subgraph "Business Logic Layer"
        CC[Charge Calculator]
        POS[Position Management]
        ORD[Order Management]
        MD[Market Data Processor]
        MARG[Margin Calculator]
        WATCH[Watchlist Manager]
    end

    %% Data Layer
    subgraph "Data Layer"
        PG[(PostgreSQL DB)]
        CSV[Instrument Master CSV]
        CACHE[Redis Cache]
    end

    %% Infrastructure Layer
    subgraph "Infrastructure Layer"
        DOCKER[Docker Containers]
        VOL[Persistent Volumes]
        NET[Traefik/Network]
    end

    %% Connections
    UI --> NGINX
    NGINX --> API
    API --> AUTH
    API --> WS
    API --> SCHED
    
    API --> CC
    API --> POS
    API --> ORD
    API --> MD
    API --> MARG
    API --> WATCH
    
    CC --> PG
    POS --> PG
    ORD --> PG
    MD --> PG
    MARG --> PG
    WATCH --> PG
    
    MD --> DHAN
    MD --> NSE
    MD --> BSE
    MD --> MCX
    
    SCHED --> CSV
    API --> PG
    API --> CACHE
    
    DOCKER --> VOL
    DOCKER --> NET
```

---

## 🔄 Data Flow Architecture

```mermaid
flowchart TD
    %% User Interaction Flow
    USER[User] --> UI[React UI]
    UI --> API[FastAPI Backend]
    
    %% Market Data Flow
    DHAN[DhanHQ] --> WS[WebSocket Manager]
    WS --> MD[Market Data Processor]
    MD --> PG[(PostgreSQL)]
    MD --> UI[Real-time Updates]
    
    %% Order Flow
    UI --> ORD[Order Service]
    ORD --> POS[Position Service]
    ORD --> CC[Charge Calculator]
    POS --> CC
    CC --> PG
    POS --> PG
    
    %% Background Processing
    SCHED[Scheduler] --> INSTR[Instrument Refresh]
    SCHED --> MARG[Margin Update]
    SCHED --> CLOSE[Price Rollover]
    INSTR --> PG
    MARG --> PG
    CLOSE --> PG
```

---

## 🏗️ Component Architecture Flowchart

```mermaid
graph LR
    subgraph "Frontend Components"
        subgraph "UI Components"
            DASH[Dashboard]
            PORTF[Portfolio]
            ORD_UI[Orders]
            POS_UI[Positions]
            WATCH_UI[Watchlist]
            CHARGES[Charges View]
        end
        
        subgraph "State Management"
            AUTH_CTX[Auth Context]
            DATA_CTX[Data Context]
            WS_CTX[WebSocket Context]
        end
    end

    subgraph "Backend Services"
        subgraph "API Routes"
            AUTH_R[Auth Routes]
            MARKET_R[Market Data Routes]
            ORDER_R[Order Routes]
            POS_R[Position Routes]
            CHARGE_R[Charge Routes]
        end
        
        subgraph "Core Services"
            AUTH_S[Auth Service]
            MARKET_S[Market Service]
            ORDER_S[Order Service]
            POS_S[Position Service]
            CHARGE_S[Charge Service]
        end
    end

    subgraph "Data Models"
        USER_M[User Model]
        ORDER_M[Order Model]
        POS_M[Position Model]
        INSTR_M[Instrument Model]
        CHARGE_M[Charge Model]
    end

    %% Frontend Connections
    DASH --> AUTH_CTX
    PORTF --> DATA_CTX
    ORD_UI --> WS_CTX
    POS_UI --> DATA_CTX
    WATCH_UI --> WS_CTX
    CHARGES --> DATA_CTX

    %% Backend Connections
    AUTH_R --> AUTH_S
    MARKET_R --> MARKET_S
    ORDER_R --> ORDER_S
    POS_R --> POS_S
    CHARGE_R --> CHARGE_S

    %% Data Model Connections
    AUTH_S --> USER_M
    ORDER_S --> ORDER_M
    POS_S --> POS_M
    MARKET_S --> INSTR_M
    CHARGE_S --> CHARGE_M
```

---

## 📈 Trading Flow Process

```mermaid
sequenceDiagram
    participant U as User
    participant UI as React UI
    participant API as FastAPI
    participant CC as Charge Calculator
    participant DB as PostgreSQL
    participant DHAN as DhanHQ

    %% Login Flow
    U->>UI: Login Request
    UI->>API: POST /auth/login
    API->>DB: Validate User
    DB-->>API: User Data
    API-->>UI: JWT Token
    UI-->>U: Logged In

    %% Market Data Flow
    DHAN->>API: Real-time Data
    API->>UI: WebSocket Push
    UI->>U: Update Prices

    %% Order Placement Flow
    U->>UI: Place Order
    UI->>API: POST /orders
    API->>CC: Calculate Charges
    CC->>API: Charge Details
    API->>DB: Save Order
    API->>DHAN: Execute Order
    DHAN-->>API: Order Confirmation
    API->>DB: Update Status
    API-->>UI: Order Result
    UI-->>U: Order Placed

    %% Position Update Flow
    DHAN->>API: Position Update
    API->>CC: Recalculate Charges
    CC->>API: Updated Charges
    API->>DB: Save Position
    API->>UI: WebSocket Update
    UI->>U: Position Updated
```

---

## 🧮 Charge Calculation Flow

```mermaid
flowchart TD
    START[Position Data] --> SEGMENT{Determine Segment}
    
    SEGMENT -->|Equity Intraday| EQUITY_INTRA[Equity Intraday Logic]
    SEGMENT -->|Equity Delivery| EQUITY_DEL[Equity Delivery Logic]
    SEGMENT -->|Index Futures| IDX_FUT[Index Futures Logic]
    SEGMENT -->|Stock Futures| STK_FUT[Stock Futures Logic]
    SEGMENT -->|Index Options| IDX_OPT[Index Options Logic]
    SEGMENT -->|Stock Options| STK_OPT[Stock Options Logic]
    SEGMENT -->|Commodity Futures| COMM_FUT[Commodity Futures Logic]
    SEGMENT -->|Commodity Options| COMM_OPT[Commodity Options Logic]

    EQUITY_INTRA --> STT[STT Calculation]
    EQUITY_DEL --> STT
    IDX_FUT --> STT
    STK_FUT --> STT
    IDX_OPT --> STT
    STK_OPT --> STT
    COMM_FUT --> STT
    COMM_OPT --> STT

    STT --> STAMP[Stamp Duty Calculation]
    STAMP --> DP[DP Charges Check]
    DP --> EXCH[Exchange Charges]
    EXCH --> SEBI[SEBI Charges]
    SEBI --> CLEAR[Clearing Charges]
    CLEAR --> GST[GST Calculation]
    GST --> TOTAL[Total Charges]
    TOTAL --> DB[(Save to Database)]
```

---

## 🐳 Docker Deployment Flow

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Local Development]
        DEV_DB[(Local DB)]
        DEV_ENV[.env.local]
    end

    subgraph "Docker Build Process"
        DOCKERFILE[Dockerfile]
        COMPOSE[docker-compose.yml]
        BUILD[Build Images]
    end

    subgraph "Container Runtime"
        PG_CONTAINER[PostgreSQL Container]
        API_CONTAINER[FastAPI Container]
        UI_CONTAINER[Nginx Container]
    end

    subgraph "Production Infrastructure"
        VPS[VPS Server]
        COOLIFY[Coolify Platform]
        TRAEFIK[Traefik Reverse Proxy]
        DOMAIN[Custom Domain]
    end

    DEV --> DOCKERFILE
    DEV --> COMPOSE
    DOCKERFILE --> BUILD
    COMPOSE --> BUILD
    BUILD --> PG_CONTAINER
    BUILD --> API_CONTAINER
    BUILD --> UI_CONTAINER
    
    PG_CONTAINER --> VPS
    API_CONTAINER --> VPS
    UI_CONTAINER --> VPS
    VPS --> COOLIFY
    COOLIFY --> TRAEFIK
    TRAEFIK --> DOMAIN
```

---

## 📊 Database Schema Flow

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email
        string name
        string role
        timestamp created_at
        timestamp updated_at
    }

    INSTRUMENTS {
        string symbol PK
        string name
        string exchange
        string segment
        decimal lot_size
        decimal tick_size
        timestamp created_at
    }

    ORDERS {
        uuid id PK
        uuid user_id FK
        string symbol FK
        string order_type
        string side
        decimal quantity
        decimal price
        string status
        timestamp created_at
        timestamp updated_at
    }

    POSITIONS {
        uuid id PK
        uuid user_id FK
        string symbol FK
        decimal quantity
        decimal avg_price
        decimal current_price
        decimal pnl
        string segment
        timestamp created_at
        timestamp updated_at
    }

    CHARGES {
        uuid id PK
        uuid position_id FK
        decimal brokerage
        decimal stt
        decimal stamp_duty
        decimal exchange_charges
        decimal sebi_charges
        decimal dp_charges
        decimal gst
        decimal total_charges
        timestamp calculated_at
    }

    WATCHLISTS {
        uuid id PK
        uuid user_id FK
        string symbol FK
        timestamp added_at
    }

    USERS ||--o{ ORDERS : places
    USERS ||--o{ POSITIONS : holds
    USERS ||--o{ WATCHLISTS : maintains
    INSTRUMENTS ||--o{ ORDERS : references
    INSTRUMENTS ||--o{ POSITIONS : references
    INSTRUMENTS ||--o{ WATCHLISTS : contains
    POSITIONS ||--o{ CHARGES : incurs
```

---

## 🔄 WebSocket Communication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant WS as WebSocket Manager
    participant MD as Market Data
    participant DHAN as DhanHQ
    participant DB as Database

    %% Connection Setup
    C->>WS: WebSocket Connect
    WS->>DB: Validate Token
    DB-->>WS: User Validated
    WS-->>C: Connection Established

    %% Market Data Subscription
    C->>WS: Subscribe to Symbol
    WS->>DHAN: Subscribe to Data
    DHAN-->>WS: Real-time Data
    WS->>MD: Process Tick Data
    MD-->>WS: Processed Data
    WS-->>C: Push Update

    %% Position Updates
    DHAN->>WS: Position Change
    WS->>DB: Update Position
    DB-->>WS: Updated Data
    WS-->>C: Position Update

    %% Error Handling
    DHAN--xWS: Connection Error
    WS->>WS: Reconnect Logic
    WS->>DHAN: Reconnect
    WS-->>C: Status Update
```

---

## 🚀 Deployment Pipeline Flow

```mermaid
graph LR
    subgraph "Development"
        CODE[Code Changes]
        TEST[Unit Tests]
        LINT[Code Quality]
    end

    subgraph "Build"
        BUILD[Docker Build]
        SCAN[Security Scan]
        TAG[Version Tag]
    end

    subgraph "Staging"
        DEPLOY_STAG[Staging Deploy]
        INTEGRATION[Integration Tests]
        E2E[E2E Tests]
    end

    subgraph "Production"
        DEPLOY_PROD[Production Deploy]
        MONITOR[Health Monitoring]
        ROLLBACK[Rollback if Needed]
    end

    CODE --> TEST
    TEST --> LINT
    LINT --> BUILD
    BUILD --> SCAN
    SCAN --> TAG
    TAG --> DEPLOY_STAG
    DEPLOY_STAG --> INTEGRATION
    INTEGRATION --> E2E
    E2E --> DEPLOY_PROD
    DEPLOY_PROD --> MONITOR
    MONITOR --> ROLLBACK
```

---

## 📱 User Journey Flow

```mermaid
journey
    title User Trading Journey
    section Registration
      Sign Up: 5: User
      Email Verification: 3: User
      Profile Setup: 4: User
    section Onboarding
      Dashboard Tour: 4: User
      Connect Broker: 3: User
      Set Preferences: 4: User
    section Trading
      Market Analysis: 5: User
      Place Order: 4: User
      Monitor Position: 5: User
      View Charges: 4: User
    section Portfolio
      View Holdings: 5: User
      P&L Analysis: 4: User
      Tax Reports: 3: User
```

---

## 🔧 Configuration Management Flow

```mermaid
graph TD
    ENV[.env File] --> CONFIG[Config Parser]
    CONFIG --> DB_CONFIG[Database Config]
    CONFIG --> API_CONFIG[API Config]
    CONFIG --> DHAN_CONFIG[DhanHQ Config]
    CONFIG --> CORS_CONFIG[CORS Config]

    DB_CONFIG --> POOL[Connection Pool]
    API_CONFIG --> FASTAPI[FastAPI App]
    DHAN_CONFIG --> CLIENT[Dhan Client]
    CORS_CONFIG --> MIDDLEWARE[CORS Middleware]

    POOL --> DB[(PostgreSQL)]
    FASTAPI --> ROUTES[API Routes]
    CLIENT --> STREAMS[Data Streams]
    MIDDLEWARE --> SECURITY[Security Headers]
```

---

## 📊 Monitoring & Logging Flow

```mermaid
graph TB
    subgraph "Application Layer"
        API_LOGS[API Logs]
        WS_LOGS[WebSocket Logs]
        SCHED_LOGS[Scheduler Logs]
    end

    subgraph "Infrastructure Layer"
        DOCKER_LOGS[Container Logs]
        NGINX_LOGS[Nginx Logs]
        DB_LOGS[Database Logs]
    end

    subgraph "Monitoring"
        HEALTH[Health Checks]
        METRICS[Performance Metrics]
        ALERTS[Alert System]
    end

    subgraph "Aggregation"
        LOG_AGG[Log Aggregator]
        METRIC_STORE[Metrics Store]
        DASHBOARD[Monitoring Dashboard]
    end

    API_LOGS --> LOG_AGG
    WS_LOGS --> LOG_AGG
    SCHED_LOGS --> LOG_AGG
    DOCKER_LOGS --> LOG_AGG
    NGINX_LOGS --> LOG_AGG
    DB_LOGS --> LOG_AGG

    HEALTH --> METRIC_STORE
    METRICS --> METRIC_STORE
    ALERTS --> METRIC_STORE

    LOG_AGG --> DASHBOARD
    METRIC_STORE --> DASHBOARD
```

---

## 🎯 Key Features Flow Summary

### Core Trading Features
- **Real-time Market Data**: WebSocket-based live price feeds
- **Order Management**: Complete order lifecycle management
- **Position Tracking**: Real-time position updates with P&L
- **Charge Calculation**: Statutory compliant charge calculations
- **Watchlist Management**: Customizable watchlists

### Technical Features
- **Microservices Architecture**: Modular, scalable design
- **Docker Deployment**: Containerized deployment
- **Database Persistence**: PostgreSQL with proper schema
- **Authentication**: JWT-based secure authentication
- **Real-time Updates**: WebSocket for live data

### Business Features
- **Multi-Exchange Support**: NSE, BSE, MCX integration
- **Multiple Segments**: Equity, Futures, Options, Commodities
- **Statutory Compliance**: SEBI/NSE/BSE/MCX compliant
- **User Management**: Role-based access control
- **Reporting**: Comprehensive charge and P&L reports

---

## 📈 Performance Optimization Flow

```mermaid
graph LR
    subgraph "Frontend Optimization"
        CODE_SPLIT[Code Splitting]
        LAZY_LOAD[Lazy Loading]
        CACHE_STRAT[Cache Strategy]
    end

    subgraph "Backend Optimization"
        DB_POOL[Connection Pooling]
        REDIS_CACHE[Redis Caching]
        ASYNC_TASK[Async Processing]
    end

    subgraph "Infrastructure Optimization"
        CDN[CDN Distribution]
        LOAD_BAL[Load Balancing]
        AUTO_SCALE[Auto Scaling]
    end

    CODE_SPLIT --> PERFORMANCE[Improved Performance]
    LAZY_LOAD --> PERFORMANCE
    CACHE_STRAT --> PERFORMANCE
    
    DB_POOL --> PERFORMANCE
    REDIS_CACHE --> PERFORMANCE
    ASYNC_TASK --> PERFORMANCE
    
    CDN --> PERFORMANCE
    LOAD_BAL --> PERFORMANCE
    AUTO_SCALE --> PERFORMANCE
```

---

## 🔒 Security Architecture Flow

```mermaid
graph TD
    subgraph "Authentication Layer"
        JWT[JWT Tokens]
        REFRESH[Token Refresh]
        SESSION[Session Management]
    end

    subgraph "Authorization Layer"
        RBAC[Role-Based Access]
        PERMISSIONS[Permission System]
        API_KEYS[API Key Management]
    end

    subgraph "Data Security"
        ENCRYPTION[Data Encryption]
        HASHING[Password Hashing]
        SANITIZATION[Input Sanitization]
    end

    subgraph "Network Security"
        CORS[CORS Policies]
        RATE_LIMIT[Rate Limiting]
        FIREWALL[Firewall Rules]
    end

    JWT --> RBAC
    REFRESH --> SESSION
    SESSION --> PERMISSIONS
    
    RBAC --> ENCRYPTION
    PERMISSIONS --> HASHING
    API_KEYS --> SANITIZATION
    
    ENCRYPTION --> CORS
    HASHING --> RATE_LIMIT
    SANITIZATION --> FIREWALL
```

---

## 📋 Summary

This comprehensive flowchart illustrates the **Trading Nexus** platform's complete architecture, covering:

1. **System Architecture**: Multi-layered design with clear separation of concerns
2. **Data Flow**: Real-time data processing and storage
3. **Component Architecture**: Modular frontend and backend components
4. **Trading Process**: Complete order-to-position lifecycle
5. **Charge Calculation**: Statutory compliant charge processing
6. **Deployment**: Docker-based containerized deployment
7. **Database Design**: Relational schema with proper relationships
8. **Communication**: WebSocket-based real-time updates
9. **Pipeline**: CI/CD deployment workflow
10. **User Journey**: Complete user experience flow
11. **Configuration**: Environment and configuration management
12. **Monitoring**: Comprehensive logging and monitoring
13. **Performance**: Multi-layer optimization strategies
14. **Security**: End-to-end security architecture

The platform is designed for **scalability**, **security**, and **regulatory compliance** while providing an excellent **user experience** for trading activities.
