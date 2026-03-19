"""
egresados_migrate.py  v2
────────────────────────
Migra egresados.db (SQLite) → MySQL Workbench

Uso:
    pip install pymysql          (solo la primera vez)
    python egresados_migrate.py
"""

import sys, subprocess

# Auto-instalar pymysql si falta
try:
    import pymysql
    import pymysql.cursors
except ImportError:
    print("📦  Instalando pymysql...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
    import pymysql
    import pymysql.cursors

import sqlite3, json
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────

SQLITE_PATH = "egresados.db"   # debe estar en la misma carpeta que este script

MYSQL_CONFIG = {
    "host":        "localhost",
    "port":        3306,
    "user":        "root",      # ← cambia si usas otro usuario
    "password":    "Ajas1500?",          # ← pon tu contraseña de MySQL aquí
    "database":    "egresados_tecnm",
    "charset":     "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

# Campos que en SQLite pueden contener JSON serializado
JSON_FIELDS = {
    "razon_eleccion_ito", "tipo_beca", "certificacion_idioma",
    "factores_empleo", "tipo_publicaciones"
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def sqlite_rows(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()

def safe_json(val):
    if val is None:
        return None
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    try:
        parsed = json.loads(val)
        return json.dumps(parsed, ensure_ascii=False)
    except (TypeError, ValueError):
        return val

# ── Migración ─────────────────────────────────────────────────────────────────

def migrate():
    print("📂  Conectando a SQLite:", SQLITE_PATH)
    if not Path(SQLITE_PATH).exists():
        print("❌  No se encontró egresados.db.")
        print("    Asegúrate de ejecutar este script desde la carpeta del proyecto.")
        return

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row

    print("🔌  Conectando a MySQL:", MYSQL_CONFIG["host"], "/", MYSQL_CONFIG["database"])
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    except Exception as e:
        print(f"❌  No se pudo conectar a MySQL: {e}")
        print("    Verifica host, usuario y contraseña en MYSQL_CONFIG.")
        return

    try:
        # ── Usuarios ──────────────────────────────────────────────────────────
        print("\n── Migrando tabla: usuarios ──")
        cols, rows = sqlite_rows(sqlite_conn, "usuarios")
        with mysql_conn.cursor() as cur:
            for row in rows:
                data = dict(zip(cols, row))
                col_names    = ", ".join(f"`{c}`" for c in data)
                placeholders = ", ".join(["%s"] * len(data))
                update_part  = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in data if c != "id")
                sql = (f"INSERT INTO usuarios ({col_names}) VALUES ({placeholders}) "
                       f"ON DUPLICATE KEY UPDATE {update_part}")
                cur.execute(sql, list(data.values()))
        mysql_conn.commit()
        print(f"   ✅  {len(rows)} usuario(s) migrado(s)")

        # ── Egresados ─────────────────────────────────────────────────────────
        print("\n── Migrando tabla: egresados ──")
        cols, rows = sqlite_rows(sqlite_conn, "egresados")
        with mysql_conn.cursor() as cur:
            for i, row in enumerate(rows, 1):
                data = dict(zip(cols, row))
                for f in JSON_FIELDS:
                    if f in data:
                        data[f] = safe_json(data[f])

                col_names    = ", ".join(f"`{c}`" for c in data)
                placeholders = ", ".join(["%s"] * len(data))
                update_part  = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in data if c != "id")
                sql = (f"INSERT INTO egresados ({col_names}) VALUES ({placeholders}) "
                       f"ON DUPLICATE KEY UPDATE {update_part}")
                cur.execute(sql, list(data.values()))
                if i % 50 == 0:
                    print(f"   … {i} registros procesados")

        mysql_conn.commit()
        print(f"   ✅  {len(rows)} egresado(s) migrado(s)")

    except Exception as e:
        mysql_conn.rollback()
        print(f"\n❌  Error: {e}")
        raise
    finally:
        sqlite_conn.close()
        mysql_conn.close()

    print("\n🎉  Migración completada con éxito.")

if __name__ == "__main__":
    migrate()