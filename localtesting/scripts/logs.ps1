#!/usr/bin/env pwsh
<#
.SYNOPSIS
    View logs from specific services

.DESCRIPTION
    This script shows logs from one or more services

.PARAMETER Services
    Array of service names to show logs for

.PARAMETER Follow
    Follow the logs in real-time

.EXAMPLE
    .\logs.ps1 -Services "postgres","redis"
    .\logs.ps1 -Services "api-gateway" -Follow
#>

param(
    [Parameter(Mandatory=$true)]
    [string[]]$Services,
    
    [switch]$Follow = $false
)

# Navigate to the localtesting directory
Set-Location $PSScriptRoot\..

$followFlag = if ($Follow) { "-f" } else { "" }

Write-Host "📜 Showing logs for: $($Services -join ', ')" -ForegroundColor Green

# Try infrastructure services first
try {
    if ($Follow) {
        docker-compose -f docker-compose.infrastructure.yml logs -f $Services
    } else {
        docker-compose -f docker-compose.infrastructure.yml logs --tail=50 $Services
    }
} catch {
    # If not found in infrastructure, try application services
    try {
        if ($Follow) {
            docker-compose -f docker-compose.services.yml logs -f $Services
        } else {
            docker-compose -f docker-compose.services.yml logs --tail=50 $Services
        }
    } catch {
        Write-Host "❌ Could not find logs for services: $($Services -join ', ')" -ForegroundColor Red
        Write-Host "Available services:" -ForegroundColor Yellow
        
        Write-Host "Infrastructure:" -ForegroundColor Blue
        docker-compose -f docker-compose.infrastructure.yml ps --services
        
        Write-Host "Application:" -ForegroundColor Blue
        docker-compose -f docker-compose.services.yml ps --services
    }
}
