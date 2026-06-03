@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo No existe el entorno virtual .venv.
    echo Ejecuta primero INSTALAR_DEPENDENCIAS.bat.
    pause
    exit /b 1
)

echo Iniciando AVSAware / SuperMercado ONIX...
".venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo La aplicacion se cerro con error.
    echo Revisa que MySQL este activo y que la base avsaware_supermercado exista.
    pause
)
