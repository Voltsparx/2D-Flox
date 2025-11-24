# Sync APK assets into the 2D-Flox assets folder
$src = Join-Path -Path $PSScriptRoot -ChildPath "..\dual\assets"
$dest = Join-Path -Path $PSScriptRoot -ChildPath "assets"

if (-not (Test-Path $src)) {
    Write-Host "Source assets folder not found: $src"
    exit 1
}

if (-not (Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest | Out-Null
}

Get-ChildItem -Path $src -File | ForEach-Object {
    $dstFile = Join-Path $dest $_.Name
    Copy-Item -Path $_.FullName -Destination $dstFile -Force
    Write-Host "Copied: $($_.Name)"
}

Write-Host "Sync complete."
