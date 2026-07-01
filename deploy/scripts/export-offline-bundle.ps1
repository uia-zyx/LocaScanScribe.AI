#Requires -Version 5.1
<#
.SYNOPSIS
  Export all Docker images required by OpenLocalSearchParser into deploy/offline/images/*.tar.gz

.DESCRIPTION
  Builds local images, pulls third-party images, tags offline copies, and saves each image
  as a gzip-compressed tar archive plus manifest.json for offline import.

.EXAMPLE
  .\deploy\scripts\export-offline-bundle.ps1
#>
param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$OutputDir = "",
    [string]$ProjectName = "openlocalsearchparser"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Ensure-PortsEnv {
    param([string]$DeployDir)
    $portsExample = Join-Path $DeployDir "ports.example.env"
    $portsEnv = Join-Path $DeployDir "ports.env"
    if (-not (Test-Path $portsEnv)) {
        Copy-Item $portsExample $portsEnv
        Write-Host "Created deploy/ports.env from ports.example.env"
    }
    return $portsEnv
}

function Save-DockerImageTarGz {
    param(
        [string]$ImageTag,
        [string]$OutputFile
    )

    $tempTar = [System.IO.Path]::ChangeExtension($OutputFile, ".tar")
    if (Test-Path $tempTar) { Remove-Item $tempTar -Force }
    if (Test-Path $OutputFile) { Remove-Item $OutputFile -Force }

    Write-Host "  saving $ImageTag -> $(Split-Path -Leaf $OutputFile)"
    & docker save $ImageTag -o $tempTar
    if ($LASTEXITCODE -ne 0) {
        throw "docker save failed for $ImageTag"
    }

    $inputStream = [System.IO.File]::OpenRead($tempTar)
    try {
        $outputStream = [System.IO.File]::Create($OutputFile)
        try {
            $gzip = New-Object System.IO.Compression.GZipStream(
                $outputStream,
                [System.IO.Compression.CompressionLevel]::Optimal
            )
            try {
                $inputStream.CopyTo($gzip)
            }
            finally {
                $gzip.Dispose()
            }
        }
        finally {
            $outputStream.Dispose()
        }
    }
    finally {
        $inputStream.Dispose()
        Remove-Item $tempTar -Force
    }
}

Push-Location $ProjectRoot
try {
    $deployDir = Join-Path $ProjectRoot "deploy"
    if (-not $OutputDir) {
        $OutputDir = Join-Path $deployDir "offline\images"
    }
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

    $portsEnv = Ensure-PortsEnv -DeployDir $deployDir
    $composeArgs = @(
        "compose",
        "--env-file", $portsEnv,
        "-f", (Join-Path $deployDir "docker-compose.yml"),
        "-p", $ProjectName
    )

    Write-Step "Building application images"
    & docker @composeArgs build
    if ($LASTEXITCODE -ne 0) { throw "docker compose build failed" }

    Write-Step "Pulling third-party images"
    & docker @composeArgs pull postgres qdrant redis minio llama-ocr llama-embedding
    if ($LASTEXITCODE -ne 0) { throw "docker compose pull failed" }

    $builtBackend = "${ProjectName}-backend"
    $builtWorker = "${ProjectName}-worker"
    $builtFrontend = "${ProjectName}-frontend"

    $offlineBackend = "openlocalsearchparser/backend:offline"
    $offlineWorker = "openlocalsearchparser/worker:offline"
    $offlineFrontend = "openlocalsearchparser/frontend:offline"

    Write-Step "Tagging offline images"
    & docker tag $builtBackend $offlineBackend
    & docker tag $builtWorker $offlineWorker
    & docker tag $builtFrontend $offlineFrontend

    $images = @(
        @{ file = "backend.tar.gz"; tag = $offlineBackend },
        @{ file = "worker.tar.gz"; tag = $offlineWorker },
        @{ file = "frontend.tar.gz"; tag = $offlineFrontend },
        @{ file = "postgres-16-alpine.tar.gz"; tag = "postgres:16-alpine" },
        @{ file = "qdrant.tar.gz"; tag = "qdrant/qdrant:latest" },
        @{ file = "redis-7-alpine.tar.gz"; tag = "redis:7-alpine" },
        @{ file = "minio.tar.gz"; tag = "minio/minio:latest" },
        @{ file = "llama-cpp-server-cuda.tar.gz"; tag = "ghcr.io/ggml-org/llama.cpp:server-cuda" }
    )

    Write-Step "Saving images to $OutputDir"
    foreach ($entry in $images) {
        $outPath = Join-Path $OutputDir $entry.file
        Save-DockerImageTarGz -ImageTag $entry.tag -OutputFile $outPath
    }

    $manifest = [ordered]@{
        version = 1
        created_at = (Get-Date).ToUniversalTime().ToString("o")
        project_name = $ProjectName
        images = $images
    }

    $manifestPath = Join-Path $OutputDir "manifest.json"
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8

    Write-Step "Done"
    Write-Host "Offline bundle ready in: $OutputDir"
    Write-Host "Copy deploy/offline/images, deploy/ports.env, model/, and .env to the target machine."
}
finally {
    Pop-Location
}
