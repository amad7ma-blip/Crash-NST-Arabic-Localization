param(
    [string]$GameDir = "",
    [switch]$Yes,
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"

function Finish-Exit([int]$Code) {
    if (-not $NoPause) {
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
    exit $Code
}

function Get-FileSha256([string]$Path) {
    return (Get-FileHash -Path $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Find-GameDirectory([string]$ExplicitDir) {
    $exeName = "CrashBandicootNSaneTrilogy.exe"
    if ($ExplicitDir -and (Test-Path (Join-Path $ExplicitDir $exeName))) {
        return (Resolve-Path $ExplicitDir).Path
    }

    $candidates = New-Object System.Collections.Generic.List[string]
    $candidates.Add($PSScriptRoot)
    $candidates.Add((Split-Path -Parent $PSScriptRoot))

    foreach ($regPath in @("HKCU:\Software\Valve\Steam", "HKLM:\SOFTWARE\WOW6432Node\Valve\Steam", "HKLM:\SOFTWARE\Valve\Steam")) {
        if (Test-Path $regPath) {
            $props = Get-ItemProperty $regPath -ErrorAction SilentlyContinue
            foreach ($propName in @("SteamPath", "InstallPath")) {
                $val = $props.$propName
                if ($val) {
                    $steamRoot = $val -replace "/", "\"
                    $candidates.Add((Join-Path $steamRoot "steamapps\common\Crash Bandicoot - N Sane Trilogy"))
                    $vdf = Join-Path $steamRoot "steamapps\libraryfolders.vdf"
                    if (Test-Path $vdf) {
                        $content = Get-Content -Path $vdf -Raw -ErrorAction SilentlyContinue
                        if ($content) {
                            $matches = [regex]::Matches($content, '"path"\s+"([^"]+)"')
                            foreach ($m in $matches) {
                                $lib = $m.Groups[1].Value -replace "\\\\", "\"
                                $candidates.Add((Join-Path $lib "steamapps\common\Crash Bandicoot - N Sane Trilogy"))
                            }
                        }
                    }
                }
            }
        }
    }

    $candidates.Add("C:\Program Files (x86)\Steam\steamapps\common\Crash Bandicoot - N Sane Trilogy")
    $candidates.Add("C:\Program Files\Steam\steamapps\common\Crash Bandicoot - N Sane Trilogy")

    foreach ($dir in ($candidates | Select-Object -Unique)) {
        if ($dir -and (Test-Path (Join-Path $dir $exeName))) {
            return (Resolve-Path $dir).Path
        }
    }
    return ""
}

Write-Host "=============================================================="
Write-Host "  Crash Bandicoot N. Sane Trilogy - Arabic Localization Pack"
Write-Host "=============================================================="

$manifestPath = Join-Path $PSScriptRoot "manifest.json"
$srcPak = Join-Path $PSScriptRoot "data\update.pak"
if (-not (Test-Path $manifestPath) -or -not (Test-Path $srcPak)) {
    Write-Host "[ERROR] Package files missing (manifest.json or data\update.pak)." -ForegroundColor Red
    Finish-Exit 1
}

$manifest = Get-Content -Path $manifestPath -Raw | ConvertFrom-Json

Write-Host "[1/5] Verifying package integrity (data\update.pak)..."
$srcSha = Get-FileSha256 $srcPak
if ($srcSha -ne $manifest.update_pak_sha256.ToLowerInvariant()) {
    Write-Host "[ERROR] data\update.pak SHA-256 mismatch! Package may be corrupted." -ForegroundColor Red
    Write-Host "  Expected: $($manifest.update_pak_sha256)"
    Write-Host "  Actual  : $srcSha"
    Finish-Exit 1
}
Write-Host "  OK: SHA-256 verified ($($srcSha.Substring(0, 16))...)"

Write-Host "[2/5] Locating game installation..."
$resolvedGameDir = Find-GameDirectory $GameDir
if (-not $resolvedGameDir) {
    if ($Yes) {
        Write-Host "[ERROR] Could not auto-detect Crash Bandicoot N. Sane Trilogy directory." -ForegroundColor Red
        Finish-Exit 1
    }
    $resolvedGameDir = Read-Host "Enter full path to 'Crash Bandicoot - N Sane Trilogy'"
    $resolvedGameDir = $resolvedGameDir.Trim('"')
}
if (-not $resolvedGameDir -or -not (Test-Path (Join-Path $resolvedGameDir $manifest.target_exe))) {
    Write-Host "[ERROR] Game executable not found in: $resolvedGameDir" -ForegroundColor Red
    Finish-Exit 1
}
Write-Host "  Found: $resolvedGameDir"

$running = Get-Process -Name "CrashBandicootNSaneTrilogy" -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "[ERROR] Game is currently running. Please close the game before installing." -ForegroundColor Red
    Finish-Exit 1
}

$archivesDir = Join-Path $resolvedGameDir "archives"
if (-not (Test-Path $archivesDir)) {
    Write-Host "[ERROR] Missing 'archives' directory in game folder." -ForegroundColor Red
    Finish-Exit 1
}

Write-Host "[3/5] Checking core original game files (SHA-256)..."
$mismatchCount = 0
foreach ($prop in $manifest.core_original_hashes.PSObject.Properties) {
    $rel = $prop.Name
    $expected = $prop.Value.ToLowerInvariant()
    $fp = Join-Path $resolvedGameDir $rel
    if (-not (Test-Path $fp)) {
        Write-Host "  [WARN] Missing expected file: $rel" -ForegroundColor Yellow
        $mismatchCount++
    } else {
        $actual = Get-FileSha256 $fp
        if ($actual -ne $expected) {
            Write-Host "  [WARN] Version/hash differs on: $rel" -ForegroundColor Yellow
            $mismatchCount++
        }
    }
}
if ($mismatchCount -gt 0) {
    Write-Host "  [WARN] $mismatchCount baseline file(s) differed from tested Steam build." -ForegroundColor Yellow
    if (-not $Yes) {
        $ans = Read-Host "Continue anyway? (y/N)"
        if ($ans -notin @("y", "Y", "yes", "YES")) {
            Finish-Exit 1
        }
    }
} else {
    $coreCount = @($manifest.core_original_hashes.PSObject.Properties).Count
    Write-Host "  OK: All $coreCount core baseline files match original SHA-256."
}

Write-Host "[4/5] Checking destination and preserving backups..."
$dstPak = Join-Path $resolvedGameDir $manifest.override_relpath
$backupDir = Join-Path $resolvedGameDir "_arabic_backup"
$markerPath = Join-Path $backupDir "installed_marker.json"
$origBackupPak = Join-Path $backupDir "original_update.pak"
$preexistingSha = ""

try {
    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }
    $probe = Join-Path $archivesDir ".write_probe.tmp"
    [IO.File]::WriteAllText($probe, "ok")
    Remove-Item $probe -Force
} catch {
    Write-Host "[ERROR] Insufficient write permissions in '$resolvedGameDir'." -ForegroundColor Red
    Write-Host "  Please right-click Install-Arabic.bat and choose 'Run as administrator'." -ForegroundColor Yellow
    Finish-Exit 1
}

if (Test-Path $dstPak) {
    $existingSha = Get-FileSha256 $dstPak
    if ($existingSha -eq $srcSha) {
        Write-Host "  Existing update.pak already matches this Arabic pack (re-verifying marker)."
    } elseif (Test-Path $markerPath) {
        Write-Host "  Existing Arabic mod update.pak detected; updating in-place (preserving any original backup)."
    } else {
        Write-Host "  Pre-existing non-mod update.pak detected; backing up cleanly to _arabic_backup\original_update.pak..."
        Copy-Item -Path $dstPak -Destination $origBackupPak -Force
        $preexistingSha = $existingSha
    }
} elseif (Test-Path $origBackupPak) {
    $preexistingSha = Get-FileSha256 $origBackupPak
}

Write-Host "[5/5] Installing non-destructive Arabic override pack (archives\update.pak)..."
Copy-Item -Path $srcPak -Destination $dstPak -Force
$installedSha = Get-FileSha256 $dstPak
if ($installedSha -ne $srcSha) {
    Write-Host "[ERROR] Installed file SHA-256 verification failed!" -ForegroundColor Red
    Finish-Exit 1
}

$marker = [ordered]@{
    package_name = $manifest.name
    version = $manifest.version
    installed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    game_dir = $resolvedGameDir
    installed_pak_rel = $manifest.override_relpath
    installed_pak_sha256 = $installedSha
    had_preexisting_update_pak = (Test-Path $origBackupPak)
    preexisting_update_pak_sha256 = $preexistingSha
}
$marker | ConvertTo-Json -Depth 4 | Set-Content -Path $markerPath -Encoding UTF8

Write-Host ""
Write-Host "SUCCESS! Crash Bandicoot N. Sane Trilogy Arabic localization installed." -ForegroundColor Green
Write-Host "  Installed: $dstPak"
Write-Host "  SHA-256  : $installedSha"
Write-Host "  Original .pak archives and Steam save files were NOT modified."
Write-Host "  You can uninstall anytime via Uninstall-Arabic.bat."
Finish-Exit 0
