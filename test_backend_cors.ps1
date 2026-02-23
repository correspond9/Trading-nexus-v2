# Test backend connectivity and CORS
$backendUrl = "http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io/api/v2"
$frontendUrl = "http://ko8ws0gg08ccwkk04oc4o0go.72.62.228.112.sslip.io"

Write-Host "===== BACKEND API TEST =====" -ForegroundColor Cyan

# Test 1: Health
Write-Host "`n[1] Health Check"
$health = curl.exe -s "$backendUrl/health" | ConvertFrom-Json
Write-Host "  Database: $($health.database)"
Write-Host "  Dhan API: $($health.dhan_api)"

# Test 2: Login  
Write-Host "`n[2] Login Test"
$loginJson = curl.exe -s -X POST "$backendUrl/auth/login" -H "Content-Type: application/json" -d '{\"mobile\":\"9999999999\",\"password\":\"admin123\"}'
$login = $loginJson | ConvertFrom-Json
Write-Host "  Role: $($login.role)"
Write-Host "  User ID: $($login.user_id)"

# Test 3: Users List
Write-Host "`n[3] Users List"
$usersJson = curl.exe -s "$backendUrl/admin/users" -H "Authorization: Bearer $($login.access_token)"
$users = $usersJson | ConvertFrom-Json
Write-Host "  Total Users: $($users.data.Count)"
foreach ($user in $users.data) {
    Write-Host "    #$($user.user_no): $($user.mobile) - $($user.role)" -ForegroundColor Green
}

# Test 4: CORS Headers
Write-Host "`n[4] CORS Headers Test"
$corsTest = curl.exe -s -i -H "Origin: $frontendUrl" "$backendUrl/health" 2>&1
$allowOrigin = $corsTest | Select-String "access-control-allow-origin" -CaseSensitive:$false
Write-Host "  Access-Control-Allow-Origin: $allowOrigin"

if ($allowOrigin) {
    Write-Host "  ✓ CORS headers present" -ForegroundColor Green
} else {
    Write-Host "  ✗ CORS headers MISSING!" -ForegroundColor Red
}

Write-Host "`n===== TEST COMPLETE =====" -ForegroundColor Cyan
