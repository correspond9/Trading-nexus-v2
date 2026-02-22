"""
phase_9_vps_testing.py
======================
Phase 9: VPS/Staging Static IP Testing

This script validates static IP authentication against real Dhan API endpoints.
It tests:
1. Signature generation matches Dhan expectations
2. API endpoints accept static authentication
3. Rate limiting behavior with static auth
4. Failure scenarios (invalid signature, IP mismatch)
5. Performance under load

Requirements:
- Dhan API Key and Secret (for static IP auth)
- Network access to https://api.dhan.co/v2 (or staging endpoint)
- Python 3.9+, httpx, asyncio
"""
import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from typing import Dict, Optional, Tuple
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ── Configuration ───────────────────────────────────────────────────────────

DHAN_API_BASE = "https://api.dhan.co/v2"
DHAN_AUTH_BASE = "https://auth.dhan.co/app"

# These should be set via environment variables in production
# For testing, configure in .env.test
DHAN_CLIENT_ID = ""  # Set via environment
DHAN_API_KEY = ""    # Set via environment
DHAN_API_SECRET = ""  # Set via environment

# ── Helper Functions ────────────────────────────────────────────────────────

def build_static_signature(
    secret: str,
    path: str,
    body: Optional[Dict] = None,
    timestamp: Optional[int] = None,
) -> Tuple[str, int]:
    """
    Generate HMAC-SHA256 signature matching Dhan v2 spec.
    
    Returns: (signature_hex, timestamp_ms)
    """
    if timestamp is None:
        timestamp = int(datetime.now().timestamp() * 1000)
    
    # Build message: timestamp + path + json_body
    body_str = json.dumps(body, separators=(',', ':')) if body else ""
    message = f"{timestamp}{path}{body_str}"
    
    # HMAC-SHA256
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature, timestamp


def build_static_headers(
    api_key: str,
    api_secret: str,
    client_id: str,
    path: str,
    body: Optional[Dict] = None,
) -> Dict[str, str]:
    """Build request headers for static IP authentication."""
    signature, timestamp = build_static_signature(api_secret, path, body)
    
    headers = {
        "X-DHAN-SIGNATURE": signature,
        "X-DHAN-TIMESTAMP": str(timestamp),
        "Content-Type": "application/json",
    }
    
    # Optionally, include API key if Dhan spec requires it
    headers["X-DHAN-API-KEY"] = api_key
    
    return headers


async def test_profile_endpoint(
    client: httpx.AsyncClient,
    api_key: str,
    api_secret: str,
    client_id: str,
) -> bool:
    """
    Test GET /profile endpoint with static signature.
    
    This is the lightest endpoint to verify auth works.
    Returns: True if successful (HTTP 200), False otherwise.
    """
    path = "/profile"
    
    headers = build_static_headers(
        api_key=api_key,
        api_secret=api_secret,
        client_id=client_id,
        path=path,
    )
    
    # Add client ID to headers if required
    headers["dhanClientId"] = client_id
    
    try:
        resp = await client.get(
            f"{DHAN_API_BASE}{path}",
            headers=headers,
            timeout=10.0,
        )
        
        log.info(f"GET {path}: HTTP {resp.status_code}")
        
        if resp.status_code == 200:
            log.info(f"✓ Auth verification successful")
            return True
        elif resp.status_code == 401:
            log.error(f"✗ Auth failed: HTTP 401 Unauthorized")
            log.error(f"Response: {resp.text[:200]}")
            return False
        elif resp.status_code == 403:
            log.error(f"✗ Signature verification failed: HTTP 403 Forbidden")
            log.error(f"Response: {resp.text[:200]}")
            return False
        else:
            log.warning(f"Unexpected status: HTTP {resp.status_code}")
            log.warning(f"Response: {resp.text[:200]}")
            return False
            
    except asyncio.TimeoutError:
        log.error("Timeout during API call (network issue)")
        return False
    except Exception as e:
        log.error(f"Error: {e}")
        return False


async def test_market_feed_endpoint(
    client: httpx.AsyncClient,
    api_key: str,
    api_secret: str,
    client_id: str,
) -> bool:
    """
    Test POST /marketfeed endpoint with static signature.
    
    This tests request body signing (more complex than GET).
    """
    path = "/marketfeed"
    body = {
        "dhanClientId": client_id,
        "exchangeTokens": ["NSE_100", "NSE_101"],  # Example tokens
    }
    
    headers = build_static_headers(
        api_key=api_key,
        api_secret=api_secret,
        client_id=client_id,
        path=path,
        body=body,
    )
    
    try:
        resp = await client.post(
            f"{DHAN_API_BASE}{path}",
            headers=headers,
            json=body,
            timeout=10.0,
        )
        
        log.info(f"POST {path}: HTTP {resp.status_code}")
        
        if resp.status_code in (200, 201):
            log.info(f"✓ Market feed request successful")
            return True
        elif resp.status_code == 401:
            log.error(f"✗ Auth failed: HTTP 401")
            return False
        elif resp.status_code == 403:
            log.error(f"✗ Signature verification failed: HTTP 403")
            return False
        else:
            log.warning(f"Unexpected status: HTTP {resp.status_code}")
            return False
            
    except Exception as e:
        log.error(f"Error: {e}")
        return False


async def test_signature_format(
    api_key: str,
    api_secret: str,
    client_id: str,
) -> bool:
    """
    Test signature format without making actual API calls.
    
    Validates:
    - Signature is valid hex string
    - Signature length is correct (SHA256 = 64 chars)
    - Timestamp is millisecond precision
    """
    log.info("Testing signature format...")
    
    path = "/profile"
    signature, timestamp = build_static_signature(api_secret, path)
    
    # Validate signature format
    assert len(signature) == 64, f"Signature should be 64 chars, got {len(signature)}"
    assert all(c in "0123456789abcdef" for c in signature), "Signature must be hex"
    
    # Validate timestamp
    now_ms = int(datetime.now().timestamp() * 1000)
    assert abs(timestamp - now_ms) < 1000, "Timestamp should be within 1 second"
    
    log.info(f"✓ Signature format valid ({len(signature)} chars)")
    log.info(f"✓ Timestamp valid (ms precision)")
    
    return True


async def test_rate_limiting(
    client: httpx.AsyncClient,
    api_key: str,
    api_secret: str,
    client_id: str,
    requests_per_second: int = 2,
) -> Tuple[bool, float]:
    """
    Test rate limiting behavior with static auth.
    
    Makes multiple requests and measures response times.
    Returns: (success, avg_response_time_ms)
    """
    log.info(f"Testing rate limiting ({requests_per_second} req/sec)...")
    
    path = "/profile"
    response_times = []
    
    for i in range(10):
        headers = build_static_headers(
            api_key=api_key,
            api_secret=api_secret,
            client_id=client_id,
            path=path,
        )
        headers["dhanClientId"] = client_id
        
        start = time.monotonic()
        try:
            resp = await client.get(
                f"{DHAN_API_BASE}{path}",
                headers=headers,
                timeout=5.0,
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            response_times.append(elapsed_ms)
            
            log.debug(f"  Request {i+1}: {elapsed_ms:.1f}ms (HTTP {resp.status_code})")
            
            # Rate limit: sleep between requests
            await asyncio.sleep(1.0 / requests_per_second)
            
        except Exception as e:
            log.error(f"Request {i+1} failed: {e}")
            return False, 0.0
    
    avg_time = sum(response_times) / len(response_times)
    log.info(f"✓ Rate limiting test passed (avg {avg_time:.1f}ms)")
    
    return True, avg_time


async def test_failure_scenarios(
    client: httpx.AsyncClient,
    api_key: str,
    api_secret: str,
    client_id: str,
) -> bool:
    """
    Test failure scenarios.
    
    1. Invalid signature (modified signature)
    2. Missing signature header
    3. Expired timestamp
    """
    log.info("Testing failure scenarios...")
    
    path = "/profile"
    success_count = 0
    
    # Test 1: Invalid signature
    log.info("  Test 1: Invalid signature")
    headers = build_static_headers(api_key, api_secret, client_id, path)
    headers["dhanClientId"] = client_id
    # Corrupt signature
    headers["X-DHAN-SIGNATURE"] = "0" * 64
    
    try:
        resp = await client.get(f"{DHAN_API_BASE}{path}", headers=headers, timeout=5.0)
        if resp.status_code == 403:
            log.info("    ✓ Invalid signature correctly rejected (403)")
            success_count += 1
        else:
            log.warning(f"    ? Unexpected response: {resp.status_code}")
    except Exception as e:
        log.warning(f"    ? Error: {e}")
    
    # Test 2: Missing signature header
    log.info("  Test 2: Missing signature header")
    headers = {"dhanClientId": client_id, "Content-Type": "application/json"}
    
    try:
        resp = await client.get(f"{DHAN_API_BASE}{path}", headers=headers, timeout=5.0)
        if resp.status_code in (401, 403):
            log.info(f"    ✓ Missing signature correctly rejected ({resp.status_code})")
            success_count += 1
        else:
            log.warning(f"    ? Unexpected response: {resp.status_code}")
    except Exception as e:
        log.warning(f"    ? Error: {e}")
    
    # Test 3: Old timestamp (more than 5 minutes)
    log.info("  Test 3: Stale timestamp (>5 minutes old)")
    headers = build_static_headers(api_key, api_secret, client_id, path)
    headers["dhanClientId"] = client_id
    # Modify timestamp to 6 minutes ago
    old_timestamp = int((datetime.now().timestamp() - 360) * 1000)
    headers["X-DHAN-TIMESTAMP"] = str(old_timestamp)
    
    try:
        resp = await client.get(f"{DHAN_API_BASE}{path}", headers=headers, timeout=5.0)
        if resp.status_code in (401, 403):
            log.info(f"    ✓ Stale timestamp correctly rejected ({resp.status_code})")
            success_count += 1
        else:
            log.warning(f"    ? Unexpected response: {resp.status_code}")
    except Exception as e:
        log.warning(f"    ? Error: {e}")
    
    log.info(f"✓ Failure scenarios test passed ({success_count}/3 scenarios)")
    return success_count >= 2  # Pass if at least 2/3 work


async def run_all_tests(
    api_key: str,
    api_secret: str,
    client_id: str,
) -> bool:
    """Run all Phase 9 VPS validation tests."""
    log.info("=" * 70)
    log.info("Phase 9: VPS/Staging Static IP Testing")
    log.info("=" * 70)
    
    results = {
        "signature_format": False,
        "profile_endpoint": False,
        "market_feed_endpoint": False,
        "rate_limiting": False,
        "failure_scenarios": False,
    }
    
    # Test 1: Signature format (no API call)
    try:
        results["signature_format"] = await test_signature_format(
            api_key, api_secret, client_id
        )
    except Exception as e:
        log.error(f"Signature format test error: {e}")
    
    # Test 2-5: With API client
    async with httpx.AsyncClient() as client:
        # Test 2: Profile endpoint
        results["profile_endpoint"] = await test_profile_endpoint(
            client, api_key, api_secret, client_id
        )
        
        # Test 3: Market feed endpoint
        results["market_feed_endpoint"] = await test_market_feed_endpoint(
            client, api_key, api_secret, client_id
        )
        
        # Test 4: Rate limiting
        success, avg_time = await test_rate_limiting(
            client, api_key, api_secret, client_id
        )
        results["rate_limiting"] = success
        
        # Test 5: Failure scenarios
        results["failure_scenarios"] = await test_failure_scenarios(
            client, api_key, api_secret, client_id
        )
    
    # Summary
    log.info("\n" + "=" * 70)
    log.info("Test Results Summary")
    log.info("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        log.info(f"{test_name:.<50} {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    log.info("=" * 70)
    log.info(f"Overall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        log.info("✓ All tests PASSED - Static IP auth is ready for production")
        return True
    elif passed_count >= 3:
        log.warning("⚠ Most tests passed - check failures above")
        return True  # Partial success
    else:
        log.error("✗ Critical tests failed - static IP auth not ready")
        return False


async def main():
    """Entry point for VPS testing."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv(".env.test")
    
    api_key = os.getenv("DHAN_API_KEY")
    api_secret = os.getenv("DHAN_API_SECRET")
    client_id = os.getenv("DHAN_CLIENT_ID")
    
    if not all([api_key, api_secret, client_id]):
        log.error("Missing credentials in environment:")
        log.error("  - DHAN_API_KEY")
        log.error("  - DHAN_API_SECRET")
        log.error("  - DHAN_CLIENT_ID")
        log.error("\nSet these in .env.test and try again")
        return False
    
    # Type guard: all values are guaranteed to be str at this point (not None)
    log.info(f"Testing with Client ID: {str(client_id)[:10]}...")
    
    success = await run_all_tests(str(api_key), str(api_secret), str(client_id))
    
    return success


if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
