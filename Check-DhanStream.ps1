# Check DhanHQ stream status and configuration
$VPS_HOST = "72.62.228.112"
$VPS_USER = "root"
$APP_UUID = "p488ok8g8swo4ockks040ccg"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "DHAN STREAM & WEBSOCKET STATUS CHECK" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Get DhanHQ status from API
Write-Host "Testing DhanHQ stream status via API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://api.tradingnexus.pro/api/v2/admin/dhan/status" `
        -Headers @{"X-AUTH" = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"} `
        -TimeoutSec 10 `
        -ErrorAction Stop
    
    $status = $response.Content | ConvertFrom-Json
    Write-Host "✓ DhanHQ Status Response:" -ForegroundColor Green
    $status | ConvertTo-Json | Write-Host
}
catch {
    Write-Host "❌ Could not get DhanHQ status: $_" -ForegroundColor Red
}

# Get stream status
Write-Host "`nTesting stream status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://api.tradingnexus.pro/api/v2/market/stream-status" `
        -Headers @{"X-AUTH" = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"} `
        -TimeoutSec 10 `
        -ErrorAction Stop
    
    $streamStatus = $response.Content | ConvertFrom-Json
    Write-Host "✓ Stream Status Response:" -ForegroundColor Green
    $streamStatus | ConvertTo-Json | Write-Host
}
catch {
    Write-Host "❌ Could not get stream status: $_" -ForegroundColor Red
}

# Test WebSocket connection
Write-Host "`nTesting WebSocket /ws/feed endpoint..." -ForegroundColor Yellow

$webSocketTest = @'
import asyncio
import websockets
import json

async def test_websocket():
    """Test connecting to WebSocket and subscribing to some tokens"""
    try:
        # Connect to WebSocket
        uri = "wss://api.tradingnexus.pro/api/v2/ws/feed"
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✓ Connected to WebSocket")
            
            # Send a subscribe message with a few common instruments
            subscribe_msg = {
                "action": "subscribe",
                "tokens": [1693509, 1693697]  # NIFTY 50, BANKNIFTY options or futures
            }
            
            print(f"Sending subscribe message: {json.dumps(subscribe_msg)}")
            await websocket.send(json.dumps(subscribe_msg))
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                print(f"✓ Received response: {response[:100]}...")
                return True
            except asyncio.TimeoutError:
                print("⚠ No response within 3 seconds (stream may not be running)")
                return False
                
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

result = asyncio.run(test_websocket())
if result:
    print("\n✓ WebSocket connection working!")
else:
    print("\n⚠ WebSocket not receiving data - streams may not be started")
'@

python -c $webSocketTest

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan
