param([string]$ProtectedDir = "C:\GuardianAI_Demo\protected")
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $RepoRoot ".venv"
& "$Venv\Scripts\python.exe" -m guardian_ai.simulator.simulate_ransomware --target $ProtectedDir
