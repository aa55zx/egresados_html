@echo off
title Detener Portal Egresados
echo.
echo  Deteniendo servidor Flask (puerto 5000)...

:: Buscar el PID que usa el puerto 5000 y terminarlo
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo  Terminando proceso PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo  [OK] Servidor detenido.
timeout /t 2 /nobreak >nul
