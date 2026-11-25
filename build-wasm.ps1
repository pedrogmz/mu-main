param (
    [switch]$RebuildAssets,
    # Only repack the Data/ and fonts/ buckets (themes, RML/RCSS, items, maps...).
    # Skips ninja, Main.data and the Main.wasm/Main.js copy: use it when no C++,
    # shader or config.ini.template change was made.
    [switch]$DataOnly
)

$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
# The proxy repo lives next to this checkout; it was renamed from
# openmu-browser-stack to open-mu-browser-proxy, so accept either name.
$workspace = Split-Path $PSScriptRoot -Parent
$stackPublic = @("open-mu-browser-proxy", "openmu-browser-stack") |
    ForEach-Object { Join-Path $workspace "$_\public" } |
    Where-Object { Test-Path $_ } |
    Select-Object -First 1
if (-not $stackPublic) { $stackPublic = Join-Path $workspace "open-mu-browser-proxy\public" }

$env:PATH = "C:\Users\Poisson\.local\dotnet;C:\Users\Poisson\.local\cmake-3.31.5-windows-x86_64\bin;C:\Users\Poisson\.local\bin;C:\Users\Poisson\emsdk;C:\Users\Poisson\emsdk\upstream\emscripten;C:\Users\Poisson\emsdk\node\24.19.0_64bit\bin;C:\Users\Poisson\emsdk\python\3.13.3_64bit;" + $env:PATH

Set-Location $repoRoot

# Configured with: cmake --preset wasm-web -B out/build/wasm-merge
# (out/build/wasm-web points at an old checkout path and no longer reconfigures).
$buildDir = "out\build\wasm-merge"

if (-not $DataOnly) {
Write-Host "=== Compiling MuMain to WebAssembly ===" -ForegroundColor Cyan
ninja -C $buildDir Main
if ($LASTEXITCODE -ne 0) {
    Write-Error "Compilation failed."
    exit $LASTEXITCODE
}

Write-Host "=== Compilation Successful ===" -ForegroundColor Green

# Main.data only carries the small, build-generated files (shaders and the
# config.ini.template that seeds config.ini in the user folder, well under 1 MB), so it is cheap to repack on every build.
# Data/ and fonts/ ship as content-addressed buckets built straight into the
# stack (see openmu-browser-stack/scripts/build-data-buckets.js): unchanged
# buckets are left untouched, so a rebuild only replaces what changed and
# browsers keep the rest cached. -RebuildAssets is kept for compatibility;
# both steps now always run.
Write-Host "=== Packaging Main.data (shaders, config.ini.template) ===" -ForegroundColor Cyan
python C:\Users\Poisson\emsdk\upstream\emscripten\tools\file_packager.py $buildDir\src\Main.data `
  --preload "$buildDir\shaders@shaders" `
  --preload "$buildDir\src\config.ini.template@config.ini.template" `
  --js-output=$buildDir\src\Main.data.js
if ($LASTEXITCODE -ne 0) {
    Write-Error "file_packager failed."
    exit $LASTEXITCODE
}
} else {
    Write-Host "=== -DataOnly: skipping compilation and Main.data ===" -ForegroundColor Yellow
}

Write-Host "=== Deploying to $stackPublic ===" -ForegroundColor Cyan
if (Test-Path $stackPublic) {
    Write-Host "=== Packaging data buckets (Data, fonts) ===" -ForegroundColor Cyan
    $bucketScript = Join-Path (Split-Path $stackPublic -Parent) "scripts\build-data-buckets.js"
    node $bucketScript --out "$stackPublic\assets" `
      --add "src\bin\Data@/Data" `
      --add "src\bin\fonts@/fonts"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Data bucket build failed."
        exit $LASTEXITCODE
    }

    if (-not $DataOnly) {
        Copy-Item "$buildDir\src\Main.wasm" "$stackPublic\Main.wasm" -Force
        Copy-Item "$buildDir\src\Main.js" "$stackPublic\Main.js" -Force
        Copy-Item "$buildDir\src\Main.data.js" "$stackPublic\Main.data.js" -Force
        Copy-Item "$buildDir\src\Main.data" "$stackPublic\Main.data" -Force
    }
    Write-Host "Deployed successfully to $stackPublic" -ForegroundColor Green
} else {
    Write-Warning "Stack public directory not found at $stackPublic"
}
