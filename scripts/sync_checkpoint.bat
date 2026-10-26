@echo off
REM Sincronizador de Etiquetas de Paracaidas (s3-b09-template)
REM Uso: scripts\sync_checkpoint.bat s3-19-start
setlocal
set TAG=%~1
if "%TAG%"=="" (
    echo Uso: scripts\sync_checkpoint.bat ^<tag^>  ^(ej. s3-19-start^)
    exit /b 1
)

if not defined UPNA_TEMPLATE_REMOTE set UPNA_TEMPLATE_REMOTE=https://github.com/Titulo-Propio-Videojuegos-UPNA/s3-b09-template.git

git fetch origin --tags --force 2>nul
git remote get-url upstream >nul 2>&1 || git remote add upstream "%UPNA_TEMPLATE_REMOTE%"
git fetch upstream --tags --force 2>nul

git rev-parse --verify "refs/tags/%TAG%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontro la etiqueta %TAG% en el repositorio ni en upstream ^(%UPNA_TEMPLATE_REMOTE%^).
    exit /b 2
)

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set TS=%%i
git branch "backup-before-%TAG%-%TS%" >nul 2>&1
git stash push -u -m "auto-stash before %TAG% (%TS%)" >nul 2>&1
git checkout -B "sesion-%TAG%" "tags/%TAG%"
echo [OK] Proyecto situado en el punto de control %TAG% (rama sesion-%TAG%).
echo      Tu avance previo ha quedado respaldado en backup-before-%TAG%-%TS%.
