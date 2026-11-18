#Requires -Version 5.1
<#
.SYNOPSIS
    Lance la demonstration LinguaFin pour le jury SAFINUM 2026.
    - Demarre le backend FastAPI (uvicorn, port 8000)
    - Attend que /health reponde (max 30 s)
    - Ouvre Microsoft Edge sur la page cible (avec repli mock_bank.html)
    - Documente la procedure de chargement manuel de l extension

.NOTES
    OS      : Windows 11
    Branch  : amelioration
    Version : 2.0
#>

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
$REPO_ROOT   = Split-Path -Parent $PSScriptRoot
$BACKEND_DIR = Join-Path $REPO_ROOT "backend"
$EXT_DIR     = Join-Path $REPO_ROOT "extension"
$MOCK_PAGE   = Join-Path $REPO_ROOT "tests\mock_bank.html"
$EDGE_EXE    = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $EDGE_EXE)) {
    $EDGE_EXE = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}
$TARGET_URL  = "https://safinum.cm/hackathon-test?jury=1"
$HEALTH_URL  = "http://127.0.0.1:8000/health"
$MAX_WAIT    = 30   # secondes

# ---------------------------------------------------------------------------
# 1. Demarrage du backend
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "=== LinguaFin Demo Launcher ===" -ForegroundColor Cyan
Write-Host "Demarrage du backend FastAPI (uvicorn, port 8000)..." -ForegroundColor Yellow

$portUsed = netstat -ano | Select-String ":8000 "
if ($portUsed) {
    Write-Host "[INFO] Le port 8000 semble deja occupe. Verification de /health..." -ForegroundColor DarkYellow
} else {
    $backendProc = Start-Process python `
        -ArgumentList "-m uvicorn backend.api:app --host 127.0.0.1 --port 8000" `
        -WorkingDirectory $REPO_ROOT `
        -PassThru `
        -WindowStyle Minimized
    Write-Host "[OK] Backend lance (PID $($backendProc.Id))" -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# 2. Attendre /health (max 30 tentatives, 1 s entre chaque)
# ---------------------------------------------------------------------------
Write-Host "Attente de /health (max $MAX_WAIT s)..." -ForegroundColor Yellow
$ok = $false
for ($i = 1; $i -le $MAX_WAIT; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-WebRequest -Uri $HEALTH_URL -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            Write-Host "[OK] Backend repond sur /health apres ${i}s" -ForegroundColor Green
            $ok = $true
            break
        }
    } catch {
        Write-Host "  Tentative $i/$MAX_WAIT..." -ForegroundColor DarkGray
    }
}

if (-not $ok) {
    Write-Host "[AVERTISSEMENT] Backend non joignable apres $MAX_WAIT s. L extension basculera en mode hors-ligne." -ForegroundColor Red
}

# ---------------------------------------------------------------------------
# 3. Verifier si le site cible est accessible (repli mock_bank.html)
# ---------------------------------------------------------------------------
$siteOk = $false
try {
    $siteResp = Invoke-WebRequest -Uri $TARGET_URL -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    if ($siteResp.StatusCode -eq 200) { $siteOk = $true }
} catch {
    Write-Host "[AVERTISSEMENT] $TARGET_URL inaccessible. Repli sur mock_bank.html local." -ForegroundColor DarkYellow
}

$pageToOpen = if ($siteOk) { $TARGET_URL } else { "file:///" + ($MOCK_PAGE -replace "\\", "/") }
Write-Host "Page cible : $pageToOpen" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 4. Tentative de chargement automatique via --load-extension (profil isole)
#
#    NOTE : Sur Edge Stable v157, --load-extension est bloque par la
#    politique de securite du profil utilisateur par defaut.
#    La seule methode fiable est un profil temporaire isole.
#    Si cette methode echoue, la procedure manuelle est imprimee.
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "Tentative de chargement automatique de l extension (profil temporaire)..." -ForegroundColor Yellow

$tempProfile = Join-Path $env:TEMP "linguafin_edge_profile_$([System.Guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Path $tempProfile -Force | Out-Null

$edgeArgs = @(
    "--user-data-dir=`"$tempProfile`""
    "--load-extension=`"$EXT_DIR`""
    "--no-first-run"
    "--disable-extensions-except=`"$EXT_DIR`""
    "`"$pageToOpen`""
)

$edgeProc = $null
$autoLoad  = $false
try {
    $edgeProc = Start-Process -FilePath $EDGE_EXE -ArgumentList $edgeArgs -PassThru -ErrorAction Stop
    Start-Sleep -Seconds 3
    if (-not $edgeProc.HasExited) {
        $autoLoad = $true
        Write-Host "[OK] Edge ouvert avec l extension chargee automatiquement (profil isole)." -ForegroundColor Green
        Write-Host "     PID Edge : $($edgeProc.Id)" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "[INFO] Chargement automatique non disponible : $_" -ForegroundColor DarkYellow
}

# ---------------------------------------------------------------------------
# 5. Procedure manuelle si le chargement automatique echoue
# ---------------------------------------------------------------------------
if (-not $autoLoad) {
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Magenta
    Write-Host "  PROCEDURE MANUELLE DE CHARGEMENT DE L EXTENSION (30 secondes)   " -ForegroundColor Magenta
    Write-Host "====================================================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  1. Dans Edge, naviguez vers :  edge://extensions" -ForegroundColor White
    Write-Host "     (ou Chrome : chrome://extensions)" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  2. Activez le curseur 'Mode developpeur'" -ForegroundColor White
    Write-Host "     (en bas a gauche sous Edge, en haut a droite sous Chrome)" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  3. Cliquez sur 'Charger les composants decompresses' (Load unpacked)" -ForegroundColor White
    Write-Host ""
    Write-Host "  4. Selectionnez le dossier :" -ForegroundColor White
    Write-Host "     $EXT_DIR" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  5. Naviguez sur : $pageToOpen" -ForegroundColor White
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Magenta
    Write-Host ""

    if (Test-Path $EDGE_EXE) {
        Start-Process -FilePath $EDGE_EXE -ArgumentList "edge://extensions"
        Start-Sleep -Milliseconds 1500
        Start-Process -FilePath $EDGE_EXE -ArgumentList "`"$pageToOpen`""
    } else {
        Start-Process "msedge" "edge://extensions"
        Start-Sleep -Milliseconds 1500
        Start-Process "msedge" "`"$pageToOpen`""
    }
}

# ---------------------------------------------------------------------------
# 6. Recapitulatif
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "=== RECAPITULATIF ===" -ForegroundColor Cyan
Write-Host "Backend             : $(if ($ok) { 'En ligne (http://127.0.0.1:8000)' } else { 'Hors ligne (catalogue embarque)' })" -ForegroundColor $(if ($ok) { 'Green' } else { 'Yellow' })
Write-Host "Site cible          : $pageToOpen"
Write-Host "Chargement auto ext : $(if ($autoLoad) { 'OUI (profil temporaire isole)' } else { 'NON - voir procedure manuelle ci-dessus' })"
Write-Host "Extension (dossier) : $EXT_DIR"
Write-Host ""
Write-Host "Pour arreter le backend : Stop-Process -Id <PID> ou fermez la fenetre uvicorn." -ForegroundColor DarkGray
Write-Host "Profile Edge temporaire supprimable : $tempProfile" -ForegroundColor DarkGray
Write-Host ""
