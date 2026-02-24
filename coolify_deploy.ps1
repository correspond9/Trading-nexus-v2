# ============================================================
# COOLIFY DEPLOYMENT SCRIPT FOR TRADING-NEXUS V2
# ============================================================
# This script automates the deployment process using Coolify API

param(
    [string]$Action = "status",  # status, create, deploy, test
    [string]$ResourceName = "trading-nexus"
)

$CoolifyUrl = "http://72.62.228.112"
$ApiToken = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
$GitRepo = "https://github.com/correspond9/Trading-nexus-v2.git"
$GitBranch = "main"

$Headers = @{
    'Authorization' = "Bearer $ApiToken"
    'Content-Type' = 'application/json'
}

# ============================================================
# FUNCTION: Get all Coolify resources
# ============================================================
function Get-CoolifyResources {
    Write-Host "`n=== FETCHING COOLIFY RESOURCES ===" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$CoolifyUrl/api/v1/resources" `
            -Headers $Headers -Method GET
        
        Write-Host "Found $($response.count) resources:" -ForegroundColor Green
        foreach ($resource in $response.resources) {
            Write-Host "  - Name: $($resource.name)" -ForegroundColor Yellow
            Write-Host "    ID: $($resource.uuid)"
            Write-Host "    Type: $($resource.type)"
            Write-Host ""
        }
        return $response.resources
    } catch {
        Write-Host "ERROR: Failed to fetch resources" -ForegroundColor Red
        Write-Host "$($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================================
# FUNCTION: Get Coolify projects
# ============================================================
function Get-CoolifyProjects {
    Write-Host "`n=== FETCHING COOLIFY PROJECTS ===" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$CoolifyUrl/api/v1/projects" `
            -Headers $Headers -Method GET
        
        Write-Host "Found $($response.count) projects:" -ForegroundColor Green
        foreach ($project in $response.projects) {
            Write-Host "  - Name: $($project.name)" -ForegroundColor Yellow
            Write-Host "    ID: $($project.uuid)"
            Write-Host ""
        }
        return $response.projects
    } catch {
        Write-Host "ERROR: Failed to fetch projects" -ForegroundColor Red
        Write-Host "$($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================================
# FUNCTION: Create new Coolify resource
# ============================================================
function New-CoolifyResource {
    param(
        [string]$ProjectId,
        [string]$EnvironmentId,
        [string]$Name
    )
    
    Write-Host "`n=== CREATING COOLIFY RESOURCE ===" -ForegroundColor Cyan
    Write-Host "Resource Name: $Name"
    Write-Host "Project ID: $ProjectId"
    Write-Host "Environment ID: $EnvironmentId"
    
    $body = @{
        name = $Name
        type = "docker"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$CoolifyUrl/api/v1/projects/$ProjectId/environments/$EnvironmentId/resources" `
            -Headers $Headers `
            -Method POST `
            -Body $body
        
        Write-Host "✓ Resource created successfully!" -ForegroundColor Green
        Write-Host "Resource ID: $($response.uuid)" -ForegroundColor Yellow
        return $response
    } catch {
        Write-Host "ERROR: Failed to create resource" -ForegroundColor Red
        Write-Host "$($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================================
# FUNCTION: Configure Git source for resource
# ============================================================
function Set-ResourceGitSource {
    param(
        [string]$ResourceId,
        [string]$Repository,
        [string]$Branch
    )
    
    Write-Host "`n=== CONFIGURING GIT SOURCE ===" -ForegroundColor Cyan
    Write-Host "Resource ID: $ResourceId"
    Write-Host "Repository: $Repository"
    Write-Host "Branch: $Branch"
    
    $body = @{
        repo = $Repository
        branch = $Branch
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$CoolifyUrl/api/v1/resources/$ResourceId/git" `
            -Headers $Headers `
            -Method POST `
            -Body $body
        
        Write-Host "✓ Git source configured!" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "ERROR: Failed to configure git source" -ForegroundColor Red
        Write-Host "$($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================================
# FUNCTION: Set environment variables
# ============================================================
function Set-ResourceEnvironmentVariables {
    param(
        [string]$ResourceId,
        [hashtable]$Variables
    )
    
    Write-Host "`n=== SETTING ENVIRONMENT VARIABLES ===" -ForegroundColor Cyan
    
    $envContent = ""
    foreach ($key in $Variables.Keys) {
        $envContent += "$key=$($Variables[$key])`n"
        Write-Host "  $key=***" -ForegroundColor Yellow
    }
    
    $body = @{
        env = $envContent
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$CoolifyUrl/api/v1/resources/$ResourceId/environment" `
            -Headers $Headers `
            -Method POST `
            -Body $body
        
        Write-Host "✓ Environment variables set!" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "ERROR: Failed to set environment variables" -ForegroundColor Red
        Write-Host "$($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================================
# FUNCTION: Deploy resource
# ============================================================
function Invoke-ResourceDeploy {
    param(
        [string]$ResourceId
    )
    
    Write-Host "`n=== STARTING DEPLOYMENT ===" -ForegroundColor Cyan
    Write-Host "Resource ID: $ResourceId"
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$CoolifyUrl/api/v1/resources/$ResourceId/deploy" `
            -Headers $Headers `
            -Method POST
        
        Write-Host "✓ Deployment started!" -ForegroundColor Green
        Write-Host "Monitor deployment in Coolify dashboard" -ForegroundColor Yellow
        return $response
    } catch {
        Write-Host "ERROR: Failed to start deployment" -ForegroundColor Red
        Write-Host "$($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================================
# FUNCTION: Get resource status
# ============================================================
function Get-ResourceStatus {
    param(
        [string]$ResourceId
    )
    
    Write-Host "`n=== CHECKING RESOURCE STATUS ===" -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$CoolifyUrl/api/v1/resources/$ResourceId" `
            -Headers $Headers `
            -Method GET
        
        Write-Host "Resource Name: $($response.name)" -ForegroundColor Yellow
        Write-Host "Status: $($response.status)"
        Write-Host "Last Error: $($response.last_error)"
        return $response
    } catch {
        Write-Host "ERROR: Failed to get status" -ForegroundColor Red
        Write-Host "$($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================================
# MAIN EXECUTION
# ============================================================
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TRADING-NEXUS V2 - COOLIFY DEPLOYMENT SCRIPT           ║" -ForegroundColor Cyan
Write-Host "║                       Version 1.0                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`nAction: $Action" -ForegroundColor Magenta
Write-Host "Coolify URL: $CoolifyUrl" -ForegroundColor Magenta
Write-Host "Git Repo: $GitRepo" -ForegroundColor Magenta
Write-Host "Git Branch: $GitBranch" -ForegroundColor Magenta

# Execute action
switch ($Action) {
    "status" {
        $resources = Get-CoolifyResources
        $projects = Get-CoolifyProjects
    }
    "create" {
        Write-Host "`nTo create a resource, you need:" -ForegroundColor Yellow
        Write-Host "  1. Project ID - status action" -ForegroundColor White
        Write-Host "  2. Environment ID - status action" -ForegroundColor White
        Write-Host "`nRun: .\coolify_deploy.ps1 -Action status" -ForegroundColor Green
    }
    default {
        Get-CoolifyResources
        Get-CoolifyProjects
    }
}

Write-Host "`n✓ Script execution complete" -ForegroundColor Green
