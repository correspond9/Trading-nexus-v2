# Test raw API responses
$backendUrl = "http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io/api/v2"

Write-Host "===== RAW API RESPONSES =====" -ForegroundColor Cyan

# Test 1: Login (raw)
Write-Host "`n[1] Login Response (RAW):"
$loginRaw = curl.exe -s -X POST "$backendUrl/auth/login" -H "Content-Type: application/json" -d '{\"mobile\":\"9999999999\",\"password\":\"admin123\"}'
Write-Host $loginRaw

# Try to parse
try {
    $login = $loginRaw | ConvertFrom-Json
    $token = $login.access_token
    Write-Host "`n  Parsed OK - Token: $($token.Substring(0,20))..." -ForegroundColor Green
} catch {
    Write-Host "`n  Parse FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit
}

# Test 2: Users (raw)
Write-Host "`n[2] Users Response (RAW first 500 chars):"
$usersRaw = curl.exe -s "$backendUrl/admin/users" -H "Authorization: Bearer $token"
Write-Host $usersRaw.Substring(0, [Math]::Min(500, $usersRaw.Length))

Write-Host "`n`n[3] Checking for Infinity/NaN:"
if ($usersRaw -match "Infinity") {
    Write-Host "  ✗ Found 'Infinity' in response!" -ForegroundColor Red
    $matches = [regex]::Matches($usersRaw, '"\w+":\s*Infinity')
    foreach ($match in $matches) {
        Write-Host "    $($match.Value)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✓ No Infinity found" -ForegroundColor Green
}
