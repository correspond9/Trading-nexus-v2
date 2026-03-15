$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

$raw = (Get-Content .\local.properties | Where-Object { $_ -like 'sdk.dir=*' }) -replace '^sdk.dir=', ''
$sdk = $raw -replace '\\:', ':' -replace '\\\\', '\'
$adb = Join-Path $sdk 'platform-tools\adb.exe'

& $adb shell am force-stop com.tradingnexus.app | Out-Null
& $adb logcat -c | Out-Null
& $adb shell am start -n com.tradingnexus.app/.MainActivity | Out-Null
Start-Sleep -Seconds 5

$logs = & $adb logcat -d -v brief
Set-Content -Path .\white-screen-logcat-coldstart.txt -Value $logs
Write-Host 'Saved logs to android\white-screen-logcat-coldstart.txt'

