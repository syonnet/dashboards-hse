@echo off
title Servidor de Dashboards Ejecutivos
cd /d "%~dp0"
echo ========================================================
echo   INICIANDO PORTAL DE DASHBOARDS (STREAMLIT)
echo ========================================================
echo.
echo Abriendo en el navegador...
echo Para detener el servidor, cierra esta ventana.
echo.

python -m streamlit run app.py
if %errorlevel% neq 0 (
    echo.
    echo Probando con ruta directa de Python...
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" -m streamlit run app.py
)
pause
