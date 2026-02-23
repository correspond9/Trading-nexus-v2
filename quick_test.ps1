$url = "http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io/api/v2"

# Login
$login = Invoke-RestMethod -Method Post -Uri "$url/auth/login" -ContentType "application/json" -Body '{"mobile":"9999999999","password":"admin123"}'
Write-Host "Login: $($login.role) (User: $($login.user_id))"

# Get users
$users = Invoke-RestMethod -Method Get -Uri "$url/admin/users" -Headers @{Authorization="Bearer $($login.access_token)"}
Write-Host "Users: $($users.data.Count)"

if ($users.data.Count -gt 0) {
    $users.data | Format-Table user_no, mobile, role, is_active -AutoSize
} else {
    Write-Host "NO USERS FOUND!" -ForegroundColor Red
}
