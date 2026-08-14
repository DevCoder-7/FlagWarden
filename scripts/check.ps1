$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "== $Name ==" -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "FAILED: $Name" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host "FlagWarden pre-push checks" -ForegroundColor Yellow

Invoke-Step "Ruff lint" { python -m ruff check . }
Invoke-Step "Ruff format check" { python -m ruff format --check . }
Invoke-Step "Pytest" { python -m pytest -q }
Invoke-Step "Bandit security scan" { python -m bandit -q -r flagwarden -x tests }
Invoke-Step "Dependency audit" { python -m pip_audit . }
Invoke-Step "Challenge pack validation" {
    python -m flagwarden.cli pack validate challenge_packs/starter-pack
}

Write-Host ""
Write-Host "All FlagWarden checks passed. Safe to commit/push." -ForegroundColor Green
