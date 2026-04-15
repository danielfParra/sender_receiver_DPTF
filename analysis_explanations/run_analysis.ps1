param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$AnalysisScript = Join-Path $ScriptDir "run_explanation_analysis.py"

if (-not (Test-Path $PythonExe)) {
    Write-Error "Python executable not found at $PythonExe"
    exit 1
}

if (-not (Test-Path $AnalysisScript)) {
    Write-Error "Analysis script not found at $AnalysisScript"
    exit 1
}

Push-Location $RepoRoot
try {
    & $PythonExe $AnalysisScript @ScriptArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
