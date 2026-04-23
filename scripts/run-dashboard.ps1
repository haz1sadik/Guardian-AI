$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $RepoRoot ".venv"
if (-not (Test-Path "$Venv\Scripts\python.exe")) {
  python -m venv $Venv
  & "$Venv\Scripts\python.exe" -m pip install --upgrade pip
  & "$Venv\Scripts\python.exe" -m pip install -r (Join-Path $RepoRoot "requirements.txt")
}
& "$Venv\Scripts\python.exe" -m uvicorn guardian_ai.dashboard.app:app --host 0.0.0.0 --port 8000
