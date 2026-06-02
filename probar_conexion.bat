@echo off
title Probar conexion Supabase
color 1F
cd /d %~dp0
echo.
.venv\Scripts\python.exe test_conexion.py
