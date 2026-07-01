#Requires -Version 5.1
<#
.SYNOPSIS
  Load Docker images from deploy/offline/images/*.tar.gz

.EXAMPLE
  .\deploy\scripts\import-offline-bundle.ps1
#>
param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ImagesDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Load-DockerImageTarGz {
    param(
        [string]$ArchiveFile
    )

    $tempTar = [System.IO.Path]::ChangeExtension($ArchiveFile, ".tar")
    if (Test-Path $tempTar) { Remove-Item $tempTar -Force }

    Write-Host "  loading $(Split-Path -Leaf $ArchiveFile)"
    $inputStream = [System.IO.File]::OpenRead($ArchiveFile)
    try {
        $outputStream = [System.IO.File]::Create($tempTar)
        try {
            $gzip = New-Object System.IO.Compression.GZipStream(
                $inputStream,
                [System.IO.Compression.CompressionMode]::Decompress
            )
            try {
                $gzip.CopyTo($outputStream)
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
    }

    & docker load -i $tempTar
    if ($LASTEXITCODE -ne 0) {
        Remove-Item $tempTar -Force -ErrorAction SilentlyContinue
        throw "docker load failed for $ArchiveFile"
    }
    Remove-Item $tempTar -Force
}

Push-Location $ProjectRoot
try {
    $deployDir = Join-Path $ProjectRoot "deploy"
    if (-not $ImagesDir) {
        $ImagesDir = Join-Path $deployDir "offline\images"
    }

    if (-not (Test-Path $ImagesDir)) {
        throw "Images directory not found: $ImagesDir"
    }

    $manifestPath = Join-Path $ImagesDir "manifest.json"
    $archives = @()

    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
        foreach ($entry in $manifest.images) {
            $archives += Join-Path $ImagesDir $entry.file
        }
    }
    else {
        $archives = Get-ChildItem -Path $ImagesDir -Filter "*.tar.gz" | ForEach-Object { $_.FullName }
    }

    if ($archives.Count -eq 0) {
        throw "No .tar.gz images found in $ImagesDir"
    }

    Write-Step "Loading $($archives.Count) image archive(s)"
    foreach ($archive in $archives) {
        if (-not (Test-Path $archive)) {
            throw "Missing archive: $archive"
        }
        Load-DockerImageTarGz -ArchiveFile $archive
    }

    Write-Step "Done"
    Write-Host "Images loaded. Run .\deploy\scripts\offline-up.ps1 to start services."
}
finally {
    Pop-Location
}
