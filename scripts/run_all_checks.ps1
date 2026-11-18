#Requires -Version 5.1
<#
.SYNOPSIS
    Execute l ensemble des suites de tests de LinguaFin SAFINUM 2026 :
    1. Backend unitaire (FastAPI, securite v2, OpenAPI, masquage, intégrité)
    2. Racine (normalisation jury, intégrité catalogue, mock bank Playwright)
    3. Accessibilité Shadow DOM (clavier, ARIA, contrastes, mobile 360px, zoom, reduced motion)
    4. Régression de performance (latences, premier rendu, absence de dérive DOM)
    5. Test Jury Live (parcours complets, injections de contenus inédits, repli skip propre si réseau hors-service)

    Affiche un tableau récapitulatif final avec le nombre de tests et le statut de chaque suite.

.NOTES
    OS      : Windows 11
    Branch  : amelioration
    Version : 2.0
#>

$ErrorActionPreference = "Continue"
$REPO_ROOT = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "    SAFINUM 2026 - LINGUAFIN : EXECUTION DE TOUTES LES SUITES        " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$results = [System.Collections.Generic.List[PSCustomObject]]::new()

function Run-Suite {
    param (
        [string]$SuiteId,
        [string]$SuiteName,
        [string]$Executable,
        [string]$Arguments
    )

    Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "[$SuiteId] $SuiteName..." -ForegroundColor Yellow
    Write-Host "Commande : $Executable $Arguments" -ForegroundColor DarkGray
    Write-Host ""

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Execution native PowerShell avec capture complete stdout + stderr
    $cmdLine = "$Executable $Arguments 2>&1"
    $rawOutput = Invoke-Expression $cmdLine
    $exitCode = $LASTEXITCODE
    $stopwatch.Stop()

    $combined = ($rawOutput | Out-String)
    $duration = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 2)

    # Afficher quelques lignes représentatives
    $lines = $combined -split "`r?`n" | Where-Object { 
        $_ -match "(Ran \d+ test|OK|FAILED|skipped=|failures=|errors=|\bPASS\b|Tests réussis|INTÈGRE|conforme)" 
    }
    foreach ($l in $lines | Select-Object -First 5) {
        Write-Host "   $l" -ForegroundColor Gray
    }

    # Extraction du nombre de tests
    $testCount = "N/A"
    if ($combined -match "Ran (\d+) test") {
        $testCount = $matches[1]
    } elseif ($combined -match "(\d+) tests?") {
        $testCount = $matches[1]
    }

    # Determination du statut
    $status = "ECHEC"
    $statusColor = "Red"
    if ($exitCode -eq 0) {
        if ($combined -match "skipped=" -and -not ($combined -match "failures=[1-9]|errors=[1-9]")) {
            $status = "OK (SKIP PARTIEL)"
            $statusColor = "DarkYellow"
        } elseif ($combined -match "\bOK\b|Toutes les vérifications.*conformes|succès") {
            $status = "SUCCES (100%)"
            $statusColor = "Green"
        } else {
            $status = "SUCCES"
            $statusColor = "Green"
        }
    } else {
        if ($combined -match "skipped=" -and -not ($combined -match "FAILED|failures=[1-9]|errors=[1-9]")) {
            $status = "IGNORE (SKIP RESEAU)"
            $statusColor = "DarkYellow"
        }
    }

    Write-Host "-> Resultat : $status (${duration}s, $testCount tests)" -ForegroundColor $statusColor
    Write-Host ""

    $results.Add([PSCustomObject]@{
        Suite         = $SuiteName
        Tests         = $testCount
        Duree_sec     = $duration
        Code_Sortie   = $exitCode
        Statut        = $status
    })
}

# 1. Backend Unitaire
Run-Suite -SuiteId "1/5" `
          -SuiteName "Backend (API, Sécurité v2, Contrat OpenAPI, Protection)" `
          -Executable "python" `
          -Arguments "-m unittest discover -s backend/tests -v"

# 2. Racine Unitaire
Run-Suite -SuiteId "2/5" `
          -SuiteName "Racine (Intégrité Jury, E2E Extension, Mock Bank Playwright)" `
          -Executable "python" `
          -Arguments "-m unittest tests/test_jury_integrity.py tests/test_extension_e2e.py tests/test_playwright_mock_bank.py -v"

# 3. Accessibilité Shadow DOM
Run-Suite -SuiteId "3/5" `
          -SuiteName "Accessibilité Widget (Clavier, ARIA, Contraste, Mobile 360px, Zoom, Reduced Motion)" `
          -Executable "python" `
          -Arguments "tests/test_widget_accessibility.py"

# 4. Performance
Run-Suite -SuiteId "4/5" `
          -SuiteName "Performance & Régression (Premier rendu, Latence, Dérive DOM)" `
          -Executable "python" `
          -Arguments "tests/test_performance_regression.py"

# 5. Jury Live
Run-Suite -SuiteId "5/5" `
          -SuiteName "Jury Live & Non-Régression (safinum.cm/hackathon-test?jury=1 ou skip propre si réseau hors-service)" `
          -Executable "python" `
          -Arguments "-m unittest tests/test_live_jury_regression.py -v"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "                     TABLEAU RECAPITULATIF FINAL                      " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$results | Format-Table -AutoSize -Property Suite, Tests, Duree_sec, Code_Sortie, Statut

$totalTests = 0
$totalDuration = 0
$allSuccess = $true
foreach ($r in $results) {
    if ($r.Tests -ne "N/A") { $totalTests += [int]$r.Tests }
    $totalDuration += [double]$r.Duree_sec
    if ($r.Code_Sortie -ne 0) { $allSuccess = $false }
}

Write-Host "Total tests executes : $totalTests" -ForegroundColor Cyan
Write-Host "Duree totale cumulee : $([Math]::Round($totalDuration, 2)) s" -ForegroundColor Cyan
if ($allSuccess) {
    Write-Host "VERDICT FINAL        : TOUTES LES SUITES SONT VALIDEES (0 ECHEC)" -ForegroundColor Green
} else {
    Write-Host "VERDICT FINAL        : AU MOINS UNE SUITE A ECHOUE" -ForegroundColor Red
}
Write-Host ""
