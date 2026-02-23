$backendUrl = "http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io/api/v2"
$output = @()

$output += "===== TESTING BACKEND API ====="
$output += ""

try {
    # Login
    $output += "[1] Login..."
    $loginBody = @{ mobile = "9999999999"; password = "admin123" } | ConvertTo-Json
    $login = Invoke-RestMethod -Method Post -Uri "$backendUrl/auth/login" -ContentType "application/json" -Body $loginBody -TimeoutSec 15
    $output += "  ✓ Success"
    $output += "    User ID: $($login.user_id)"
    $output += "    Role: $($login.role)"
    
    # Get users
    $output += ""
    $output += "[2] Fetching users..."
    $headers = @{ Authorization = "Bearer $($login.access_token)" }
    $users = Invoke-RestMethod -Method Get -Uri "$backendUrl/admin/users" -Headers $headers -TimeoutSec 15
    $output += "  ✓ Success"
    $output += "    Total users: $($users.data.Count)"
    
    if ($users.data.Count -gt 0) {
        $output += ""
        $output += "  Users:"
        foreach ($user in $users.data) {
            $output += "    #$($user.user_no): $($user.mobile) - $($user.role) (Balance: $($user.wallet_balance))"
        }
    } else {
        $output += "  ⚠ No users in database!"
    }
    
    # Check credentials
    $output += ""
    $output += "[3] Dhan credentials status..."
    $creds = Invoke-RestMethod -Method Get -Uri "$backendUrl/admin/credentials/active" -Headers $headers -TimeoutSec 15
    $output += "  Static configured: $($creds.static_configured)"
    $output += "  Auth mode: $($creds.auth_mode)"
    
} catch {
    $output += "  ✗ ERROR: $($_.Exception.Message)"
    if ($_.ErrorDetails.Message) {
        $output += "    Details: $($_.ErrorDetails.Message)"
    }
}

$output += ""
$output += "===== TEST COMPLETE ====="

# Write to file and console
$output | Out-File -FilePath "api_test_result.txt" -Encoding UTF8
$output | ForEach-Object { Write-Host $_ }
