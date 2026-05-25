$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location (Join-Path $projectRoot '..')

if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000
} else {
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
}
