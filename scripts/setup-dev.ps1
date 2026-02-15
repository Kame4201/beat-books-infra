# setup-dev.ps1 — Clone and set up all BeatTheBooks repos
# Run from the parent directory where you want all repos

$GITHUB_USER = "Kame4201"
$repos = @("beat-books-data", "beat-books-model", "beat-books-api", "beat-books-infra")

foreach ($repo in $repos) {
    if (Test-Path $repo) {
        Write-Host "$repo already exists, skipping clone" -ForegroundColor Yellow
    } else {
        Write-Host "Cloning $repo..." -ForegroundColor Cyan
        git clone "https://github.com/$GITHUB_USER/$repo.git"
    }
}

Write-Host "`nAll repos cloned. Next steps:" -ForegroundColor Green
Write-Host "1. cd beat-books-data && pip install -r requirements.txt && cp .env.example .env"
Write-Host "2. Edit .env with your DATABASE_URL"
Write-Host "3. uvicorn src.main:app --reload --port 8001"
