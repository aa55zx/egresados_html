@echo off
title Portal Egresados - TecNM Oaxaca
color 1F

echo.
echo  ============================================
echo    Portal de Egresados - TecNM Campus Oaxaca
echo  ============================================
echo.
echo  Instalando dependencias Python...
pip install flask flask-cors werkzeug pymysql --quiet

echo.
echo  Iniciando servidor Flask...
echo  Abre tu navegador en: http://localhost:5000
echo.
echo  *** CREDENCIALES ADMIN ***
echo  Usuario:    admin
echo  Contrasena: TecNM2025
echo.

python app.py

pause
