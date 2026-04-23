# Guardian-AI MVP Prototype (Windows Ransomware Demo)

This repository provides a zero-to-demo prototype aligned to your poster goals:

- Detect ransomware-like behavior quickly (Isolation Forest + burst features)
- Contain attack behavior (terminate suspicious high-write processes + apply temporary protected-folder read-only policy)
- Run folder-scoped integrity hash check
- Restore tampered/locked files from periodic backup set
- Trigger VSS snapshot attempt on each backup cycle
- Send alerts to admin dashboard on same LAN
- Auto-install/auto-start agent via PowerShell installer

## 1) Architecture

- **Victim machine (Windows 10)**
  - `guardian_ai.agent.main`
  - Watches one protected folder only (MVP scope)
  - Executes detect → contain → hash-check → restore pipeline
- **Dashboard machine (same Wi-Fi)**
  - FastAPI server + simple web page
  - Receives and displays alerts

## 2) Repository layout

- `guardian_ai/agent/` - runtime detection, backup, containment, restore
- `guardian_ai/dashboard/` - API + admin UI
- `guardian_ai/training/` - model training/evaluation/MTCR tools
- `guardian_ai/simulator/` - safe folder-scoped attack simulator
- `scripts/` - install/run scripts

## 3) Quick start (dashboard machine)

```powershell
cd <repo>
.\scripts\run-dashboard.ps1
```

Open `http://<dashboard-ip>:8000`.

## 4) Quick start (victim machine)

```powershell
cd <repo>
.\scripts\install-agent.ps1
```

Installer prompts dashboard URL (example: `http://192.168.1.20:8000`) and registers startup task `GuardianAI_Agent`.

## 5) Prepare protected demo folder

Use: `C:\GuardianAI_Demo\protected`

Put `.txt`, `.pdf`, `.docx`, `.xlsx` files for demo.

## 6) Run safe demo attack

```powershell
cd <repo>
.\scripts\run-demo-attack.ps1 -ProtectedDir "C:\GuardianAI_Demo\protected"
```

Expected:
1. Agent detects abnormal burst.
2. Agent kills top high-write candidates.
3. Agent checks hash mismatches in protected folder.
4. Agent restores changed files from latest backup mirror.
5. Alert appears on dashboard with MTCR.

## 7) Model training (Isolation Forest)

Input CSV schema (`created_rate,modified_rate,deleted_rate,renamed_rate,distinct_ext`) where rows are benign baseline windows:

```powershell
python -m guardian_ai.training.train_model --input data\benign_windows.csv --output C:\ProgramData\GuardianAI\model\isolation_forest.joblib --contamination 0.08
```

## 8) Model evaluation (offline)

Evaluation CSV requires same features + `label` (`0=benign`, `1=attack`):

```powershell
python -m guardian_ai.training.evaluate_model --model C:\ProgramData\GuardianAI\model\isolation_forest.joblib --input data\eval_windows.csv --label-col label --threshold -0.15
```

Outputs confusion matrix, precision/recall/F1, and ROC-AUC.

## 9) Real-world evaluation using MTCR

Define MTCR as:

`MTCR = restore_done_ts - detect_ts`

Collect repeated run logs with columns `detect_ts,restore_done_ts` then run:

```powershell
python -m guardian_ai.training.mtcr_eval --input data\mtcr_runs.csv
```

Report mean/min/max MTCR for panel demo.

## 10) Notes

- This is an **MVP prototype** focused on one protected folder (not system-wide).
- VSS invocation is implemented as a scheduled backup-cycle trigger attempt.
- For production-grade process attribution and richer ETW features, add dedicated ETW provider integration in next phase.
