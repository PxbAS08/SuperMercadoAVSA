@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo AVSAware / SuperMercado ONIX
echo Instalacion de dependencias
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo No se encontro Python en PATH.
    echo Instala Python 3.10 o superior y vuelve a ejecutar este archivo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
)

echo Instalando requirements.txt...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Dependencias instaladas correctamente.
echo Ahora importa la base de datos en MySQL Workbench:
echo   1. database\avsaware_schema.sql
echo   2. database\seed_data.sql
echo.
pause
