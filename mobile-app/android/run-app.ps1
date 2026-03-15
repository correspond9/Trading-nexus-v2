$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Always run from the Android project folder where gradlew.bat exists.
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

function Get-SdkDirFromLocalProperties {
    $localProps = Join-Path $projectDir 'local.properties'
    if (-not (Test-Path $localProps)) {
        return $null
    }

    $line = Get-Content $localProps | Where-Object { $_ -like 'sdk.dir=*' } | Select-Object -First 1
    if (-not $line) {
        return $null
    }

    $raw = $line -replace '^sdk.dir=', ''
    return ($raw -replace '\\:', ':' -replace '\\\\', '\')
}

function Get-AdbPath {
    $sdkDir = Get-SdkDirFromLocalProperties
    if ($sdkDir) {
        $adbFromSdk = Join-Path $sdkDir 'platform-tools\adb.exe'
        if (Test-Path $adbFromSdk) {
            return $adbFromSdk
        }
    }

    $adbCmd = Get-Command adb -ErrorAction SilentlyContinue
    if ($adbCmd) {
        return $adbCmd.Source
    }

    return $null
}

function Get-AppId {
    $appGradle = Join-Path $projectDir 'app\build.gradle'
    if (-not (Test-Path $appGradle)) {
        return 'com.tradingnexus.app'
    }

    $match = Select-String -Path $appGradle -Pattern 'applicationId\s+"([^"]+)"' | Select-Object -First 1
    if ($match -and $match.Matches.Count -gt 0) {
        return $match.Matches[0].Groups[1].Value
    }

    return 'com.tradingnexus.app'
}

Write-Host 'Step 1/4: Building debug app...' -ForegroundColor Cyan
& .\gradlew.bat :app:assembleDebug --console=plain

$adb = Get-AdbPath
if (-not $adb) {
    Write-Host 'Could not find ADB. Please install Android SDK Platform-Tools, then run this script again.' -ForegroundColor Red
    exit 1
}

Write-Host 'Step 2/4: Checking connected Android device/emulator...' -ForegroundColor Cyan
$deviceLines = & $adb devices | Select-Object -Skip 1 | Where-Object { $_ -match '\S' }
$onlineDevices = $deviceLines | Where-Object { $_ -match '\sdevice$' }

if (-not $onlineDevices) {
    Write-Host 'No online Android device found.' -ForegroundColor Yellow
    Write-Host 'Open an Android emulator (or connect a phone with USB debugging), then run this script again.' -ForegroundColor Yellow
    exit 1
}

Write-Host 'Step 3/4: Installing app on device/emulator...' -ForegroundColor Cyan
& .\gradlew.bat :app:installDebug --console=plain

$appId = Get-AppId
Write-Host "Step 4/4: Launching app ($appId)..." -ForegroundColor Cyan
& $adb shell monkey -p $appId -c android.intent.category.LAUNCHER 1 | Out-Null

Write-Host ''
Write-Host 'Done. Your app should now be open on the emulator/device.' -ForegroundColor Green

