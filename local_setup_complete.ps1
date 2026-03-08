# ================================================================
# Complete Local Setup - Run All Steps Automatically
# ================================================================
# This master script runs all 5 setup steps in sequence
# Perfect for a fresh local environment setup
# ================================================================

param(
    [switch]$SkipRebuild,    # Skip Docker rebuild if images are fresh
    [switch]$SkipExport,     # Skip production export if you have recent dump
    [switch]$Interactive     # Pause between steps for review
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║        Trading Nexus - Complete Local Setup Automation        ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║  This will set up a complete local replica of production      ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Estimate total time
$totalTimeEstimate = 20
if ($SkipRebuild) { $totalTimeEstimate -= 5 }
if ($SkipExport) { $totalTimeEstimate -= 3 }

Write-Host "⏱️  Estimated time: ~$totalTimeEstimate minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Steps to be executed:" -ForegroundColor Cyan
Write-Host "   1. Rebuild Docker images $(if ($SkipRebuild) { '(SKIPPED)' } else { '' })" -ForegroundColor Gray
Write-Host "   2. Export production database $(if ($SkipExport) { '(SKIPPED)' } else { '' })" -ForegroundColor Gray
Write-Host "   3. Import database to local" -ForegroundColor Gray
Write-Host "   4. Synchronize configuration" -ForegroundColor Gray
Write-Host "   5. Start services & verify" -ForegroundColor Gray
Write-Host ""

$continue = Read-Host "Continue? (Y/n)"
if ($continue -eq "n" -or $continue -eq "N") {
    Write-Host "Setup cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "  Starting automated setup..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

$startTime = Get-Date

# ===== STEP 1: Rebuild Docker Images =====
if (-not $SkipRebuild) {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  STEP 1/5: Rebuilding Docker Images                           ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    & .\local_setup_1_rebuild_docker.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Step 1 failed. Aborting setup." -ForegroundColor Red
        exit 1
    }
    
    if ($Interactive) {
        Write-Host ""
        Read-Host "Press Enter to continue to Step 2"
    }
} else {
    Write-Host "⏭️  STEP 1: Skipped (using existing Docker images)" -ForegroundColor Yellow
    Write-Host ""
}

# ===== STEP 2: Export Production Database =====
if (-not $SkipExport) {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  STEP 2/5: Exporting Production Database                      ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    & .\local_setup_2_export_production_db.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Step 2 failed. Aborting setup." -ForegroundColor Red
        exit 1
    }
    
    if ($Interactive) {
        Write-Host ""
        Read-Host "Press Enter to continue to Step 3"
    }
} else {
    Write-Host "⏭️  STEP 2: Skipped (using existing database dump)" -ForegroundColor Yellow
    Write-Host ""
}

# ===== STEP 3: Import Database to Local =====
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  STEP 3/5: Importing Database to Local                        ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

& .\local_setup_3_import_to_local.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Step 3 completed with warnings (usually normal)" -ForegroundColor Yellow
}

if ($Interactive) {
    Write-Host ""
    Read-Host "Press Enter to continue to Step 4"
}

# ===== STEP 4: Synchronize Configuration =====
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  STEP 4/5: Synchronizing Configuration                        ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

& .\local_setup_4_sync_config.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Step 4 failed. Aborting setup." -ForegroundColor Red
    exit 1
}

if ($Interactive) {
    Write-Host ""
    Read-Host "Press Enter to continue to Step 5"
}

# ===== STEP 5: Start Services & Verify =====
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  STEP 5/5: Starting Services & Verification                   ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

& .\local_setup_5_start_and_verify.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Step 5 completed with warnings" -ForegroundColor Yellow
}

# ===== COMPLETION =====
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalMinutes

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║              🎉 LOCAL SETUP COMPLETE! 🎉                       ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "⏱️  Total time: $([math]::Round($duration, 1)) minutes" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Your local environment is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📌 Quick Access:" -ForegroundColor Cyan
Write-Host "   • Frontend:  http://localhost" -ForegroundColor White
Write-Host "   • Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   • API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Open http://localhost in your browser" -ForegroundColor Gray
Write-Host "   2. Login with any production user credentials" -ForegroundColor Gray
Write-Host "   3. Start testing your features!" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Yellow
Write-Host "   docker compose logs -f          # View live logs" -ForegroundColor Gray
Write-Host "   docker compose down             # Stop all services" -ForegroundColor Gray
Write-Host "   docker compose restart backend  # Restart after code changes" -ForegroundColor Gray
Write-Host ""
Write-Host "Happy testing! 🚀" -ForegroundColor Cyan
Write-Host ""

# Optional: Open browser
$openBrowser = Read-Host "Open http://localhost in browser? (Y/n)"
if ($openBrowser -ne "n" -and $openBrowser -ne "N") {
    Start-Process "http://localhost"
}
