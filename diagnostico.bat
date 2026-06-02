@echo off
title Diagnostico de conexion - Supabase
color 1F
cd /d %~dp0
echo.
echo  ============================================
echo   Diagnostico de conexion a Supabase
echo  ============================================
echo.

echo  [1] Probando DNS (ping)...
ping -n 1 db.lgmckhssohxdqmhszgtn.supabase.co
echo.

echo  [2] Probando puerto 5432 (PostgreSQL directo)...
.venv\Scripts\python.exe -c "import socket; s=socket.create_connection(('db.lgmckhssohxdqmhszgtn.supabase.co',5432),timeout=5); print('  Puerto 5432: ABIERTO'); s.close()" 2>nul || echo   Puerto 5432: CERRADO o sin DNS

echo.
echo  [3] Probando puerto 6543 (Supabase pooler)...
.venv\Scripts\python.exe -c "import socket; s=socket.create_connection(('aws-0-us-east-1.pooler.supabase.com',6543),timeout=5); print('  Puerto 6543: ABIERTO'); s.close()" 2>nul || echo   Puerto 6543: CERRADO o sin DNS

echo.
echo  [4] Probando con URL de Transaction Pooler (puerto 6543)...
.venv\Scripts\python.exe -c "
import psycopg2
url = 'postgresql://postgres.lgmckhssohxdqmhszgtn:3G456G65H6H@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
try:
    conn = psycopg2.connect(url)
    print('  CONEXION EXITOSA con Transaction Pooler!')
    conn.close()
except Exception as e:
    print(f'  Error: {e}')
"

echo.
echo  [5] Probando con Session Pooler (puerto 5432 pooler)...
.venv\Scripts\python.exe -c "
import psycopg2
url = 'postgresql://postgres.lgmckhssohxdqmhszgtn:3G456G65H6H@aws-0-us-east-1.pooler.supabase.com:5432/postgres'
try:
    conn = psycopg2.connect(url)
    print('  CONEXION EXITOSA con Session Pooler!')
    conn.close()
except Exception as e:
    print(f'  Error: {e}')
"

echo.
pause
