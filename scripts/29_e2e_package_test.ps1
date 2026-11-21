$ErrorActionPreference = "Stop"

$WS = "C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic"
$GameDir = "C:\Program Files (x86)\Steam\steamapps\common\Crash Bandicoot - N Sane Trilogy"
$Py = "$WS\.venv\Scripts\python.exe"
$PkgDir = "$WS\package"
$DstPak = "$GameDir\archives\update.pak"
$Marker = "$GameDir\_arabic_backup\installed_marker.json"
$OrigBak = "$GameDir\_arabic_backup\original_update.pak"
$Manifest = Get-Content "$PkgDir\manifest.json" -Raw | ConvertFrom-Json

Write-Host "=== [1/6] Remove old temporary test_update.pak & check baseline ==="
if (Test-Path $DstPak) { Remove-Item $DstPak -Force }
if (Test-Path "$GameDir\_arabic_backup") { Remove-Item "$GameDir\_arabic_backup" -Recurse -Force }
@'
import hashlib, json, os
WS = r"C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic"
GD = r"C:\Program Files (x86)\Steam\steamapps\common\Crash Bandicoot - N Sane Trilogy"
base = json.load(open(os.path.join(WS, 'backups', 'original_hashes.json'), encoding='utf-8'))
bad = 0
for rel, info in base['files'].items():
    p = os.path.join(GD, rel)
    if not os.path.exists(p) or os.path.getsize(p) != info['size']:
        bad += 1
        print('SIZE MISMATCH:', rel)
assert bad == 0, f'{bad} original files changed size'
for rel, info in base['files'].items():
    h = hashlib.sha256()
    with open(os.path.join(GD, rel), 'rb') as f:
        while chunk := f.read(1 << 22):
            h.update(chunk)
    assert h.hexdigest() == info['sha256'], f'SHA256 mismatch on {rel}'
print(f"Verified ALL {len(base['files'])} original files match SHA-256 100% cleanly.")
'@ | & $Py -
if ($LASTEXITCODE -ne 0) { throw "Baseline check failed" }

Write-Host "=== [2/6] Clean Install test (via .bat + Steam auto-detect) ==="
& cmd.exe /c "`"$PkgDir\Install-Arabic.bat`" -Yes -NoPause"
if ($LASTEXITCODE -ne 0) { throw "Clean install failed" }
$sha1 = (Get-FileHash $DstPak -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sha1 -ne $Manifest.update_pak_sha256) { throw "Installed SHA-256 mismatch" }
if (-not (Test-Path $Marker)) { throw "Missing installed_marker.json" }

Write-Host "=== [3/6] Re-install / Idempotency test ==="
& cmd.exe /c "`"$PkgDir\Install-Arabic.bat`" -Yes -NoPause"
if ($LASTEXITCODE -ne 0) { throw "Re-install failed" }
$sha2 = (Get-FileHash $DstPak -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sha2 -ne $Manifest.update_pak_sha256) { throw "Re-installed SHA-256 mismatch" }
if (Test-Path $OrigBak) { throw "Re-install must not falsely back up own mod as original_update.pak!" }

Write-Host "=== [4/6] Full Uninstall test (via .bat + auto-detect) ==="
& cmd.exe /c "`"$PkgDir\Uninstall-Arabic.bat`" -Yes -NoPause"
if ($LASTEXITCODE -ne 0) { throw "Uninstall failed" }
if (Test-Path $DstPak) { throw "update.pak still exists after uninstall" }
if (Test-Path "$GameDir\_arabic_backup") { throw "_arabic_backup still exists after clean uninstall" }

Write-Host "=== [4b] Pre-existing update.pak backup & restore test ==="
[IO.File]::WriteAllText($DstPak, "SIMULATED_PREEXISTING_UPDATE_PAK")
$dummySha = (Get-FileHash $DstPak -Algorithm SHA256).Hash.ToLowerInvariant()
& cmd.exe /c "`"$PkgDir\Install-Arabic.bat`" -Yes -NoPause"
if ($LASTEXITCODE -ne 0) { throw "Install over preexisting update.pak failed" }
if (-not (Test-Path $OrigBak)) { throw "Pre-existing update.pak was NOT backed up!" }
& cmd.exe /c "`"$PkgDir\Uninstall-Arabic.bat`" -Yes -NoPause"
if ($LASTEXITCODE -ne 0) { throw "Uninstall restore test failed" }
$restoredSha = (Get-FileHash $DstPak -Algorithm SHA256).Hash.ToLowerInvariant()
if ($restoredSha -ne $dummySha) { throw "Restored original_update.pak SHA-256 mismatch!" }
Remove-Item $DstPak -Force

Write-Host "=== [5/6] Final Clean Install (leave ready to play) ==="
& cmd.exe /c "`"$PkgDir\Install-Arabic.bat`" -Yes -NoPause"
if ($LASTEXITCODE -ne 0) { throw "Final install failed" }
$sha3 = (Get-FileHash $DstPak -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sha3 -ne $Manifest.update_pak_sha256) { throw "Final installed SHA-256 mismatch" }
Write-Host "Final package installed & SHA-256 verified: $sha3"

Write-Host "=== [6/6] Launch verification with final compressed update.pak ==="
Start-Process "steam://rungameid/731490"
$proc = $null
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    $proc = Get-Process -Name "CrashBandicootNSaneTrilogy" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($proc) { break }
}
if (-not $proc) { throw "Game process did not start within 30s" }

# Wait 10s while game mounts update.pak & reaches menus, probe sharing lock on update.pak
Start-Sleep -Seconds 10
$proc.Refresh()
$alive = -not $proc.HasExited
$responding = $proc.Responding
$memMB = [math]::Round($proc.WorkingSet64 / 1MB, 1)
$pakLocked = $false
try {
    $fs = [IO.File]::Open($DstPak, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    $fs.Close()
} catch {
    $pakLocked = $true
}
Write-Host "Game launch result: PID=$($proc.Id) Alive=$alive Responding=$responding MemMB=$memMB UpdatePakLockedByGame=$pakLocked"

Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$still = Get-Process -Name "CrashBandicootNSaneTrilogy" -ErrorAction SilentlyContinue
if ($still) { taskkill /IM CrashBandicootNSaneTrilogy.exe /F | Out-Null }
if (-not $alive) { throw "Game exited prematurely!" }
Write-Host "ALL END-TO-END PACKAGE & LAUNCH CHECKS PASSED."
