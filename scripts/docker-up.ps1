# Start the BeatTheBooks stack using Docker Compose
# Usage: .\scripts\docker-up.ps1 [dev|test|prod]

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "test", "prod")]
    [string]$Mode = "prod"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$DockerDir = Join-Path $ProjectRoot "docker"

Set-Location $DockerDir

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✏️  Please edit docker\.env with your actual values before proceeding." -ForegroundColor Yellow
    exit 1
}

switch ($Mode) {
    "dev" {
        Write-Host "🚀 Starting BeatTheBooks stack in DEVELOPMENT mode..." -ForegroundColor Green
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
    }
    "test" {
        Write-Host "🧪 Starting BeatTheBooks stack in TEST mode..." -ForegroundColor Cyan
        docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build --abort-on-container-exit
    }
    "prod" {
        Write-Host "🚀 Starting BeatTheBooks stack in PRODUCTION mode..." -ForegroundColor Green
        docker-compose up --build
    }
}
