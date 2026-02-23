# ── Trading Nexus — Backend Dockerfile ──────────────────────────────────────
# Multi-stage: builder installs deps, final image is lean at runtime.

# ── Stage 1: dependency builder ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools needed by some Python packages (e.g. asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Only runtime libs needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/       ./app/
COPY migrations/ ./migrations/
COPY instrument_master/ ./instrument_master/

# Non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# uvicorn with 1 worker: this app starts background tasks (WS managers, pollers)
# in the lifespan, so multiple workers would duplicate outbound connections.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
    "--workers", "1", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
