$ErrorActionPreference = "Stop"

$pythonPathCandidates = @(
    "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    "C:\Users\91974\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)

$python = $null
foreach ($candidate in $pythonPathCandidates) {
    if (Test-Path $candidate) {
        $python = $candidate
        break
    }
}

if (-not $python) {
    foreach ($candidate in @("python", "py")) {
        if (-not (Get-Command $candidate -ErrorAction SilentlyContinue)) {
            continue
        }
        try {
            & $candidate -c "print('ok')" *> $null
            if ($LASTEXITCODE -eq 0) {
                $python = $candidate
                break
            }
        } catch {
            continue
        }
    }
}

if (-not $python) {
    Write-Host "Python was not found. Install Python 3.11+ or run this from Codex where the bundled runtime exists."
    exit 1
}

& $python main.py --chat --month 2026-05
