param(
  [string]$DashboardUrl = "",
  [string]$ProtectedDir = "C:\GuardianAI_Demo\protected",
  [string]$BackupDir = "C:\GuardianAI_Demo\backups\latest",
  [int]$BackupIntervalSeconds = 300
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $RepoRoot ".venv"
$ConfigDir = "C:\ProgramData\GuardianAI"
$ConfigPath = Join-Path $ConfigDir "config.json"

if (-not $DashboardUrl) {
  $DashboardUrl = Read-Host "Enter dashboard URL (e.g., http://192.168.1.10:8000)"
}

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
New-Item -ItemType Directory -Force -Path $ProtectedDir | Out-Null
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

python -m venv $VenvPath
& "$VenvPath\Scripts\python.exe" -m pip install --upgrade pip
& "$VenvPath\Scripts\python.exe" -m pip install -r (Join-Path $RepoRoot "requirements.txt")

$config = @{
  dashboard_url = $DashboardUrl
  protected_dir = $ProtectedDir
  backup_dir = $BackupDir
  model_path = "C:\ProgramData\GuardianAI\model\isolation_forest.joblib"
  manifest_path = "C:\ProgramData\GuardianAI\manifest\baseline_hashes.json"
  backup_interval_seconds = $BackupIntervalSeconds
  detection_window_seconds = 5
  anomaly_threshold = -0.15
  max_kill_candidates = 3
} | ConvertTo-Json

Set-Content -Path $ConfigPath -Value $config -Encoding UTF8

$taskName = "GuardianAI_Agent"
$pythonExe = "$VenvPath\Scripts\python.exe"
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "-m guardian_ai.agent.main"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName

Write-Host "Guardian-AI agent installed and started."
