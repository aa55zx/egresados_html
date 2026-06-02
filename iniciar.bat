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

:: Instalar dependencias (psycopg2 para Supabase/PostgreSQL)
echo  Verificando dependencias...
.venv\Scripts\pip.exe install flask flask-cors werkzeug psycopg2-binary python-dotenv --quiet
echo  [OK] Dependencias listas.
echo.

:: Verificar que python existe en el venv
if not exist ".venv\Scripts\python.exe" (
    echo  [ERROR] No se encontro Python en .venv\Scripts\python.exe
    pause
    exit /b 1
)

:: Verificar que app.py existe
if not exist "app.py" (
    echo  [ERROR] No se encontro app.py
    pause
    exit /b 1
)

echo  Iniciando servidor Flask (conectando a Supabase)...
echo.

:: Iniciar Flask en una ventana visible
start "Flask - Portal Egresados" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe app.py"

:: Esperar que Flask arranque
echo  Esperando que el servidor arranque...
set /a intentos=0
:esperar
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% == 0 goto listo
set /a intentos+=1
if %intentos% lss 15 goto esperar

echo.
echo  ============================================
echo  [ERROR] Flask no pudo arrancar.
echo  ============================================
echo.
echo  Revisa la ventana de Flask para ver el error.
echo  Causa mas comun: DATABASE_URL en .env no esta configurado.
echo  Abre el archivo .env y coloca tu URL de Supabase.
echo.
pause
exit /b 1

:listo
echo.
echo  [OK] Servidor listo en http://localhost:5000
echo.
echo  *** CREDENCIALES DE ACCESO ***
echo  Administrador:  admin     / TecNM2025
echo  Egresado:       egresado1 / Egresado2025
echo  Organizacion:   empresa1  / Empresa2025
echo.

start http://localhost:5000
pause
