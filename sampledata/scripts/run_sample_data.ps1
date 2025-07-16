#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Generate and seed sample data for Vetterati application
.DESCRIPTION
    This script installs dependencies, generates sample data, and seeds the database
#>

param(
    [int]$Candidates = 500,
    [int]$Positions = 50,
    [switch]$SkipGeneration,
    [switch]$SkipSeeding,
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\run_sample_data.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Candidates    Number of candidates to generate (default: 500)"
    Write-Host "  -Positions     Number of positions to generate (default: 50)"
    Write-Host "  -SkipGeneration Skip data generation step"
    Write-Host "  -SkipSeeding   Skip database seeding step"
    Write-Host "  -Help          Show this help message"
    exit 0
}

# Change to scripts directory
Set-Location -Path $PSScriptRoot

Write-Host "=== Vetterati Sample Data Generator ===" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
try {
    python -m pip install -r requirements.txt
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Generate sample data
if (-not $SkipGeneration) {
    Write-Host ""
    Write-Host "Generating sample data..." -ForegroundColor Yellow
    Write-Host "Candidates: $Candidates" -ForegroundColor Cyan
    Write-Host "Positions: $Positions" -ForegroundColor Cyan
    
    try {
        # Modify the Python script to accept command line arguments
        $env:NUM_CANDIDATES = $Candidates
        $env:NUM_POSITIONS = $Positions
        
        python generate_sample_data.py
        Write-Host "Sample data generated successfully" -ForegroundColor Green
    } catch {
        Write-Host "Error: Failed to generate sample data" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Skipping data generation..." -ForegroundColor Yellow
}

# Seed database
if (-not $SkipSeeding) {
    Write-Host ""
    Write-Host "Seeding database..." -ForegroundColor Yellow
    
    # Check if Docker services are running
    try {
        $dockerStatus = docker-compose -f ../../docker-compose.yml ps --services --filter "status=running"
        if ($dockerStatus -notcontains "postgres") {
            Write-Host "Warning: PostgreSQL service may not be running. Starting services..." -ForegroundColor Yellow
            Set-Location -Path "../.."
            docker-compose up -d postgres
            Set-Location -Path "sampledata/scripts"
            Start-Sleep -Seconds 10
        }
    } catch {
        Write-Host "Warning: Could not check Docker services status" -ForegroundColor Yellow
    }
    
    try {
        python seed_database.py
        Write-Host "Database seeded successfully" -ForegroundColor Green
    } catch {
        Write-Host "Error: Failed to seed database" -ForegroundColor Red
        Write-Host "Make sure PostgreSQL is running and accessible" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "Skipping database seeding..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Sample Data Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  - Generated $Candidates candidates" -ForegroundColor White
Write-Host "  - Generated $Positions positions" -ForegroundColor White
Write-Host "  - Seeded database with AHP match scores" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start the application services: docker-compose up -d" -ForegroundColor White
Write-Host "  2. Open the dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "  3. View the candidate matches with real data!" -ForegroundColor White
