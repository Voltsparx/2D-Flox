# prepare_release.ps1
# Copies the main Python file and available asset folders into this 2D-Flox folder
# Run this from the 2D-Flox folder in PowerShell.

$root = Join-Path -Path $PSScriptRoot -ChildPath ".."
$root = (Resolve-Path $root).Path
$src_main = Join-Path -Path $root -ChildPath "project_buzzkill.py"
$dest_main = Join-Path -Path $PSScriptRoot -ChildPath "project_buzzkill.py"

if (Test-Path $src_main) {
    Copy-Item -Path $src_main -Destination $dest_main -Force
    Write-Host "Copied main script to 2D-Flox: project_buzzkill.py"
} else {
    Write-Host "Main script not found at: $src_main"
}

# Ensure assets folder exists
$dest_assets = Join-Path $PSScriptRoot -ChildPath "assets"
if (-not (Test-Path $dest_assets)) { New-Item -ItemType Directory -Path $dest_assets | Out-Null }

# Copy from repo assets if present
$src_assets1 = Join-Path $root -ChildPath "assets"
$src_assets2 = Join-Path $root -ChildPath "dual\assets"

if (Test-Path $src_assets1) {
    Get-ChildItem -Path $src_assets1 -File | ForEach-Object { Copy-Item -Path $_.FullName -Destination (Join-Path $dest_assets $_.Name) -Force }
    Write-Host "Copied files from repo assets/."
}

if (Test-Path $src_assets2) {
    Get-ChildItem -Path $src_assets2 -File | ForEach-Object { Copy-Item -Path $_.FullName -Destination (Join-Path $dest_assets $_.Name) -Force }
    Write-Host "Copied files from dual/assets/."
}

Write-Host "Prepare complete. Check the 2D-Flox folder for a self-contained copy."