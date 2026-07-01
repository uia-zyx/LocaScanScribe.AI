#Requires -Version 5.1
<#
.SYNOPSIS
  Start OpenLocalSearchParser from pre-loaded offline images.

.EXAMPLE
  .\deploy\scripts\offline-up.ps1
#>
param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ProjectName = "openlocalsearchparser",
    [switch]$ImportImages
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

Push-Location $ProjectRoot
try {
    $deployDir = Join-Path $ProjectRoot "deploy"
    $portsExample = Join-Path $deployDir "ports.example.env"
    $portsEnv = Join-Path $deployDir "ports.env"
    if (-not (Test-Path $portsEnv)) {
        Copy-Item $portsExample $portsEnv
        Write-Host "Created deploy/ports.env from ports.example.env"
    }

    if ($ImportImages) {
        & (Join-Path $PSScriptRoot "import-offline-bundle.ps1") -ProjectRoot $ProjectRoot
    }

    $composeArgs = @(
        "compose",
        "--env-file", $portsEnv,
        "-f", (Join-Path $deployDir "docker-compose.yml"),
        "-f", (Join-Path $deployDir "docker-compose.offline.yml"),
        "-p", $ProjectName,
        "up", "-d", "--no-build"
    )

    Write-Step "Starting services (offline mode)"
    & docker @composeArgs
    if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

    $ports = @{}
    Get-Content $portsEnv | ForEach-Object {
        if ($_ -match '^\s*([A-Z0-9_]+)\s*=\s*(.+?)\s*$' -and $_ -notmatch '^\s*#') {
            $ports[$Matches[1]] = $Matches[2]
        }
    }

    $frontendPort = if ($ports.ContainsKey("OLSP_FRONTEND_HOST_PORT")) { $ports["OLSP_FRONTEND_HOST_PORT"] } else { "18473" }
    $backendPort = if ($ports.ContainsKey("OLSP_BACKEND_HOST_PORT")) { $ports["OLSP_BACKEND_HOST_PORT"] } else { "52891" }

    Write-Step "Services started"
    Write-Host "Frontend: http://localhost:$frontendPort"
    Write-Host "Backend:  http://localhost:$backendPort/docs"
    Write-Host "MCP:      http://localhost:$backendPort/mcp"
}
finally {
    Pop-Location
}
