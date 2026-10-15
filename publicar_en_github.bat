@echo off
chcp 65001 > nul
cls
echo ========================================================
echo   PUBLICADOR AUTOMÁTICO A GITHUB / STREAMLIT CLOUD
echo ========================================================
echo.

git status > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git no esta inicializado en esta carpeta.
    pause
    exit /b
)

git remote get-url origin > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo No hay ningun repositorio remoto de GitHub vinculado.
    echo.
    echo 1. Ve a https://github.com/new y crea un repositorio (vacio).
    echo 2. Copia la URL HTTPS de tu nuevo repositorio (ejemplo: https://github.com/tu-usuario/dashboards-hse.git)
    echo.
    set /p REPO_URL="Pega aqui la URL de tu repositorio de GitHub: "
    if "%REPO_URL%"=="" (
        echo [ERROR] No ingresaste ninguna URL. Operacion cancelada.
        pause
        exit /b
    )
    git remote add origin %REPO_URL%
    echo Repositorio vinculado exitosamente.
    echo.
)

echo Preparando archivos y cambios...
git branch -M main
git add .
set /p MENSAJE="Mensaje del commit (Presiona ENTER para usar 'Actualizacion de Dashboards'): "
if "%MENSAJE%"=="" set MENSAJE=Actualizacion de Dashboards

git commit -m "%MENSAJE%"
echo.
echo Subiendo cambios a GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   ¡SUBIDO EXITOSAMENTE A GITHUB!
    echo ========================================================
    echo.
    echo Pasos finales para que corra 24/7 en Streamlit Cloud:
    echo 1. Ve a: https://share.streamlit.io
    echo 2. Clic en 'New app'
    echo 3. Selecciona tu repositorio y rama 'main'
    echo 4. Main file path: app.py
    echo 5. Clic en 'Deploy'
    echo.
) else (
    echo.
    echo [AVISO] Hubo un problema al subir a GitHub. Verifica tus credenciales o permisos.
)

pause
