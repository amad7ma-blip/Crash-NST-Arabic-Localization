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
Write-Host "  Crash Bandicoot N. Sane Trilogy - Arabic Uninstaller"
Write-Host "=============================================================="

$manifestPath = Join-Path $PSScriptRoot "manifest.json"
if (-not (Test-Path $manifestPath)) {
    Write-Host "[ERROR] manifest.json missing." -ForegroundColor Red
    Finish-Exit 1
}
$manifest = Get-Content -Path $manifestPath -Raw | ConvertFrom-Json

$resolvedGameDir = Find-GameDirectory $GameDir
if (-not $resolvedGameDir) {
    if ($Yes) {
        Write-Host "[ERROR] Could not auto-detect game directory." -ForegroundColor Red
        Finish-Exit 1
    }
    $resolvedGameDir = Read-Host "Enter full path to 'Crash Bandicoot - N Sane Trilogy'"
    $resolvedGameDir = $resolvedGameDir.Trim('"')
}
if (-not $resolvedGameDir -or -not (Test-Path (Join-Path $resolvedGameDir $manifest.target_exe))) {
    Write-Host "[ERROR] Game executable not found in: $resolvedGameDir" -ForegroundColor Red
    Finish-Exit 1
}
Write-Host "[1/3] Game directory: $resolvedGameDir"

$running = Get-Process -Name "CrashBandicootNSaneTrilogy" -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "[ERROR] Game is currently running. Please close it before uninstalling." -ForegroundColor Red
    Finish-Exit 1
}

$dstPak = Join-Path $resolvedGameDir $manifest.override_relpath
$backupDir = Join-Path $resolvedGameDir "_arabic_backup"
$markerPath = Join-Path $backupDir "installed_marker.json"
$origBackupPak = Join-Path $backupDir "original_update.pak"

$marker = $null
if (Test-Path $markerPath) {
    $marker = Get-Content -Path $markerPath -Raw | ConvertFrom-Json
}

Write-Host "[2/3] Removing Arabic override / restoring original state..."
if (Test-Path $dstPak) {
    $curSha = Get-FileSha256 $dstPak
    $knownModSha = $manifest.update_pak_sha256.ToLowerInvariant()
    $markerSha = if ($marker) { $marker.installed_pak_sha256.ToLowerInvariant() } else { "" }
    if ($curSha -ne $knownModSha -and $curSha -ne $markerSha) {
        Write-Host "  [WARN] archives\update.pak does not match the recorded Arabic override SHA-256." -ForegroundColor Yellow
        if (-not $Yes) {
            $ans = Read-Host "Remove/restore archives\update.pak anyway? (y/N)"
            if ($ans -notin @("y", "Y", "yes", "YES")) {
                Finish-Exit 1
            }
        }
    }

    if (Test-Path $origBackupPak) {
        Copy-Item -Path $origBackupPak -Destination $dstPak -Force
        Remove-Item -Path $origBackupPak -Force
        Write-Host "  Restored pre-existing original archives\update.pak."
    } else {
        Remove-Item -Path $dstPak -Force
        Write-Host "  Removed Arabic override archives\update.pak."
    }
} elseif (Test-Path $origBackupPak) {
    Copy-Item -Path $origBackupPak -Destination $dstPak -Force
    Remove-Item -Path $origBackupPak -Force
    Write-Host "  Restored pre-existing original archives\update.pak."
} else {
    Write-Host "  archives\update.pak already absent."
}

if (Test-Path $markerPath) {
    Remove-Item -Path $markerPath -Force
}
if ((Test-Path $backupDir) -and ((Get-ChildItem -Path $backupDir -Force | Measure-Object).Count -eq 0)) {
    Remove-Item -Path $backupDir -Force
}

Write-Host "[3/3] Verifying core original game files against SHA-256 baseline..."
$bad = 0
foreach ($prop in $manifest.core_original_hashes.PSObject.Properties) {
    $fp = Join-Path $resolvedGameDir $prop.Name
    if (-not (Test-Path $fp) -or (Get-FileSha256 $fp) -ne $prop.Value.ToLowerInvariant()) {
        Write-Host "  [WARN] Hash mismatch on $($prop.Name)" -ForegroundColor Yellow
        $bad++
    }
}
if ($bad -eq 0) {
    $coreCount = @($manifest.core_original_hashes.PSObject.Properties).Count
    Write-Host "  OK: All core game files verified clean ($coreCount files)."
}

Write-Host ""
Write-Host "SUCCESS! Arabic localization has been completely uninstalled." -ForegroundColor Green
Write-Host "  Original game files and save data remain intact."
Finish-Exit 0
