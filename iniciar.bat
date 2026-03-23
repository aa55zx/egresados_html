@echo off
title Portal Egresados - TecNM Oaxaca
color 1F

:: ─── Verificar si Flask ya está corriendo en el puerto 5000 ───
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% == 0 (
    echo.
    echo  [OK] Flask ya esta corriendo en http://localhost:5000
    echo  Abriendo el portal en el navegador...
    timeout /t 1 /nobreak >nul
    start http://localhost:5000
    exit
)

:: ─── Flask no está corriendo, iniciarlo ───
echo.
echo  ============================================
echo    Portal de Egresados - TecNM Campus Oaxaca
echo  ============================================
echo.

:: Ir al directorio del proyecto
cd /d %~dp0

:: Instalar dependencias si faltan
echo  Verificando dependencias...
.venv\Scripts\pip.exe install flask flask-cors werkzeug pymysql python-dotenv --quiet
echo  [OK] Dependencias listas.
echo.

:: Verificar que python existe en el venv
if not exist ".venv\Scripts\python.exe" (
    echo  [ERROR] No se encontro Python en .venv\Scripts\python.exe
    echo  Asegurate de que el entorno virtual este creado.
    pause
    exit /b 1
)

:: Verificar que app.py existe
if not exist "app.py" (
    echo  [ERROR] No se encontro app.py en %~dp0
    pause
    exit /b 1
)

echo  Iniciando servidor Flask...
echo  (Se abrira una ventana con los logs de Flask)
echo.

:: Iniciar Flask en una ventana VISIBLE para ver errores
start "Flask - Portal Egresados" cmd /k "cd /d %~dp0 && echo Arrancando Flask... && .venv\Scripts\python.exe app.py"

:: Esperar a que Flask arranque (máx 12 segundos)
echo  Esperando que el servidor arranque...
set /a intentos=0
:esperar
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% == 0 goto listo
set /a intentos+=1
if %intentos% lss 12 goto esperar

echo.
echo  ============================================
echo  [ERROR] Flask no pudo arrancar en 12 segundos.
echo  ============================================
echo.
echo  Revisa la ventana de Flask que se abrio para ver el error.
echo  Causas comunes:
echo    1. MySQL no esta corriendo (abre MySQL Workbench primero)
echo    2. Contrasena incorrecta en el archivo .env
echo    3. La base de datos "egresados_tecnm" no existe
echo.
pause
exit /b 1

:listo
echo.
echo  [OK] Servidor listo en http://localhost:5000
echo.
echo  *** CREDENCIALES ***
echo  Admin:    admin / TecNM2025
echo.

:: Abrir el navegador
start http://localhost:5000

pause
