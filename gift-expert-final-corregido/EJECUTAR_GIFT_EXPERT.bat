@echo off
setlocal
chcp 65001 > nul
cd /d "%~dp0"
title Gift Expert - Python + Flask

echo ================================================================
echo   GIFT EXPERT - PREPARANDO APLICACION
echo ================================================================

set "PYTHON_CMD=python"
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"

%PYTHON_CMD% --version >nul 2>nul
if errorlevel 1 goto python_error

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creando entorno virtual...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto general_error
) else (
  echo [1/3] Entorno virtual encontrado.
)

echo [2/3] Instalando o verificando dependencias...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto general_error

echo [3/3] Iniciando servidor y abriendo el navegador...
".venv\Scripts\python.exe" launcher.py
if errorlevel 1 goto general_error
goto end

:python_error
echo.
echo ERROR: Python no esta instalado o no esta agregado al PATH.
echo Instala Python 3.10 o superior y marca la opcion "Add Python to PATH".
pause
goto end

:general_error
echo.
echo ERROR: No fue posible preparar o iniciar Gift Expert.
echo Revisa tu conexion a Internet durante la primera instalacion.
pause

:end
endlocal
