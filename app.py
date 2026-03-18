"""
Portal de Egresados — TecNM Campus Oaxaca
Backend Flask + SQLite  (con autenticación por sesión)
"""

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, json, functools
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "egresados.db")

app = Flask(__name__, static_folder=BASE_DIR)
app.secret_key = "TecNM-Oaxaca-2025-clave-secreta-cambiar-en-produccion"
CORS(app, supports_credentials=True)

# ──────────────────────────────────────────────────────────────────────────────
# Base de datos
# ──────────────────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # ── Tabla de usuarios ──────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT UNIQUE NOT NULL,
            password_hash  TEXT NOT NULL,
            nombre         TEXT NOT NULL,
            email          TEXT,
            role           TEXT NOT NULL DEFAULT 'egresado',  -- 'admin' | 'egresado'
            activo         INTEGER NOT NULL DEFAULT 1,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Crear admin por defecto si no existe
    c.execute("SELECT id FROM usuarios WHERE username='admin'")
    if not c.fetchone():
        c.execute("""
            INSERT INTO usuarios (username, password_hash, nombre, role)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            generate_password_hash("TecNM2025"),
            "Administrador TecNM",
            "admin"
        ))
        print("  👤  Admin creado  →  user: admin  |  pass: TecNM2025")

    # ── Tabla de egresados ─────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS egresados (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id                 INTEGER REFERENCES usuarios(id),
            -- ── Sección I: Demográfico ──
            nombre                  TEXT,
            sexo                    TEXT,
            estado_civil            TEXT,
            municipio               TEXT,
            ciudad                  TEXT,
            codigo_postal           TEXT,
            pais                    TEXT DEFAULT 'México',
            telefono                TEXT,
            email                   TEXT,
            dependientes_economicos TEXT,
            -- ── Sección II: Académico ──
            razon_eleccion_ito      TEXT,
            programa_posgrado       TEXT,
            linea_investigacion     TEXT,
            beca                    TEXT,
            institucion_beca        TEXT,
            tipo_beca               TEXT,
            tiempo_extra_grado      TEXT,
            causa_tiempo_extra      TEXT,
            importancia_titulacion  TEXT,
            dominio_idioma          TEXT,
            idiomas                 TEXT,
            certificacion_idioma    TEXT,
            -- ── Sección III: Laboral ──
            empleado_cursando       TEXT,
            puesto_cursando         TEXT,
            contrato_cursando       TEXT,
            cambio_empleo           TEXT,
            tiempo_conseguir_empleo TEXT,
            factores_empleo         TEXT,
            labora_actualmente      TEXT,
            tipo_institucion        TEXT,
            sector_economico        TEXT,
            tipo_contrato_actual    TEXT,
            actividades_empleo      TEXT,
            escala_coincidencia     INTEGER,
            escala_conocimientos    INTEGER,
            escala_impacto          INTEGER,
            escala_pertinencia      INTEGER,
            -- ── Sección IV: Investigación ──
            publicaciones           TEXT,
            tipo_publicaciones      TEXT,
            sni                     TEXT,
            red_tematica            TEXT,
            premios                 TEXT,
            descripcion_premios     TEXT,
            academia                TEXT,
            postdoctoral            TEXT,
            -- ── Sección V: Evaluación ──
            escala_contenidos       INTEGER,
            escala_didacticas       INTEGER,
            escala_evaluacion_doc   INTEGER,
            escala_biblio           INTEGER,
            escala_asesoria         INTEGER,
            escala_satisfaccion     INTEGER,
            escala_laboratorios     INTEGER,
            escala_biblioteca       INTEGER,
            escala_internet         INTEGER,
            escala_instalaciones    INTEGER,
            expectativas_cumplidas  TEXT,
            calidad_programa        TEXT,
            areas_mejora            TEXT,
            mejora_plan_estudios    TEXT,
            -- ── Sección VI: Actualización ──
            cursos_actualizacion    TEXT,
            descripcion_cursos      TEXT,
            actividades_deseadas    TEXT,
            tiempo_disponible       TEXT,
            empresa_propia          TEXT,
            puesto_cinco_anos       TEXT,
            cargo_eleccion          TEXT,
            descripcion_cargo       TEXT,
            -- ── Sección VII: Comentarios ──
            comentarios             TEXT,
            recomendaria            TEXT,
            fecha_encuesta          TEXT,
            -- ── Metadatos ──
            fecha_registro          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

# ──────────────────────────────────────────────────────────────────────────────
# Decoradores de autenticación
# ──────────────────────────────────────────────────────────────────────────────

def require_login(f):
    """Cualquier usuario autenticado."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        return f(*args, **kwargs)
    return wrapper

def require_admin(f):
    """Solo rol admin."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        if session.get("role") != "admin":
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        return f(*args, **kwargs)
    return wrapper

# ──────────────────────────────────────────────────────────────────────────────
# API — Autenticación
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    d = request.get_json(silent=True) or {}
    username = (d.get("username") or "").strip()
    password = d.get("password") or ""

    if not username or not password:
        return jsonify({"success": False, "error": "Usuario y contraseña requeridos"}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,))
    user = c.fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401

    session.permanent = True
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["nombre"]   = user["nombre"]
    session["role"]     = user["role"]

    return jsonify({
        "success": True,
        "user": {
            "id":       user["id"],
            "username": user["username"],
            "nombre":   user["nombre"],
            "role":     user["role"]
        }
    })


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Sesión cerrada"})


@app.route("/api/auth/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"success": False, "authenticated": False}), 401
    return jsonify({
        "success": True,
        "authenticated": True,
        "user": {
            "id":       session["user_id"],
            "username": session["username"],
            "nombre":   session["nombre"],
            "role":     session["role"]
        }
    })

# ──────────────────────────────────────────────────────────────────────────────
# API — Gestión de Usuarios (solo admin)
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
@require_admin
def list_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT id, username, nombre, email, role, activo, created_at
        FROM usuarios ORDER BY created_at DESC
    """)
    users = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": users, "total": len(users)})


@app.route("/api/users", methods=["POST"])
@require_admin
def create_user():
    d = request.get_json(silent=True) or {}
    username = (d.get("username") or "").strip()
    password = d.get("password") or ""
    nombre   = (d.get("nombre") or "").strip()
    email    = (d.get("email") or "").strip()
    role     = d.get("role", "egresado")

    if not username or not password or not nombre:
        return jsonify({"success": False, "error": "username, password y nombre son requeridos"}), 400
    if role not in ("admin", "egresado"):
        return jsonify({"success": False, "error": "role debe ser 'admin' o 'egresado'"}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM usuarios WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "El usuario ya existe"}), 409

    c.execute("""
        INSERT INTO usuarios (username, password_hash, nombre, email, role)
        VALUES (?, ?, ?, ?, ?)
    """, (username, generate_password_hash(password), nombre, email, role))
    conn.commit()
    new_id = c.lastrowid
    conn.close()

    return jsonify({"success": True, "id": new_id, "message": "Usuario creado exitosamente"})


@app.route("/api/users/<int:uid>", methods=["GET"])
@require_admin
def get_user(uid):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, nombre, email, role, activo, created_at FROM usuarios WHERE id=?", (uid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "error": "No encontrado"}), 404
    return jsonify({"success": True, "data": dict(row)})


@app.route("/api/users/<int:uid>", methods=["PUT"])
@require_admin
def update_user(uid):
    # No permitir editar al propio admin principal (id=1) si es el único admin
    d = request.get_json(silent=True) or {}
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE id=?", (uid,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "error": "No encontrado"}), 404

    nombre  = d.get("nombre", user["nombre"])
    email   = d.get("email",  user["email"])
    role    = d.get("role",   user["role"])
    activo  = d.get("activo", user["activo"])

    updates = ["nombre=?", "email=?", "role=?", "activo=?"]
    values  = [nombre, email, role, activo]

    if d.get("password"):
        updates.append("password_hash=?")
        values.append(generate_password_hash(d["password"]))

    values.append(uid)
    c.execute(f"UPDATE usuarios SET {', '.join(updates)} WHERE id=?", values)
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Usuario actualizado"})


@app.route("/api/users/<int:uid>", methods=["DELETE"])
@require_admin
def delete_user(uid):
    # Proteger al admin principal
    if uid == session.get("user_id"):
        return jsonify({"success": False, "error": "No puedes eliminar tu propia cuenta"}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, role FROM usuarios WHERE id=?", (uid,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "error": "No encontrado"}), 404
    c.execute("DELETE FROM usuarios WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Usuario eliminado"})

# ──────────────────────────────────────────────────────────────────────────────
# Helpers para egresados
# ──────────────────────────────────────────────────────────────────────────────

JSON_FIELDS = {
    "razon_eleccion_ito", "tipo_beca", "certificacion_idioma",
    "factores_empleo", "tipo_publicaciones"
}

def row_to_dict(row):
    d = dict(row)
    for f in JSON_FIELDS:
        if d.get(f):
            try:    d[f] = json.loads(d[f])
            except: pass
    return d

def serialize(v):
    if isinstance(v, list):
        return json.dumps(v, ensure_ascii=False)
    return v

# ──────────────────────────────────────────────────────────────────────────────
# API — Egresados (protegido: requiere login)
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/egresados", methods=["GET"])
@require_login
def list_egresados():
    search = request.args.get("search", "").strip()
    prog   = request.args.get("programa", "").strip()
    sector = request.args.get("sector", "").strip()
    sni_f  = request.args.get("sni", "").strip()
    page   = max(1, int(request.args.get("page", 1)))
    per    = min(50, int(request.args.get("per", 12)))

    where, params = ["1=1"], []

    if search:
        where.append("(nombre LIKE ? OR email LIKE ? OR ciudad LIKE ? OR programa_posgrado LIKE ?)")
        params += [f"%{search}%"] * 4
    if prog:
        where.append("programa_posgrado LIKE ?")
        params.append(f"%{prog}%")
    if sector:
        where.append("sector_economico LIKE ?")
        params.append(f"%{sector}%")
    if sni_f:
        where.append("sni LIKE ?")
        params.append(f"%{sni_f}%")

    base_q = f"FROM egresados WHERE {' AND '.join(where)}"
    conn   = get_db()
    c      = conn.cursor()

    c.execute(f"SELECT COUNT(*) n {base_q}", params)
    total = c.fetchone()["n"]

    c.execute(
        f"SELECT * {base_q} ORDER BY fecha_registro DESC LIMIT ? OFFSET ?",
        params + [per, (page - 1) * per]
    )
    rows = [row_to_dict(r) for r in c.fetchall()]
    conn.close()

    return jsonify({
        "success": True,
        "data":    rows,
        "total":   total,
        "page":    page,
        "per":     per,
        "pages":   max(1, -(-total // per))
    })


@app.route("/api/egresados", methods=["POST"])
@require_login
def create_egresado():
    d = request.get_json(silent=True) or {}
    if not d.get("nombre"):
        return jsonify({"success": False, "error": "El campo 'nombre' es requerido"}), 400

    COLS = [
        "nombre","sexo","estado_civil","municipio","ciudad","codigo_postal","pais",
        "telefono","email","dependientes_economicos","razon_eleccion_ito",
        "programa_posgrado","linea_investigacion","beca","institucion_beca","tipo_beca",
        "tiempo_extra_grado","causa_tiempo_extra","importancia_titulacion","dominio_idioma",
        "idiomas","certificacion_idioma","empleado_cursando","puesto_cursando",
        "contrato_cursando","cambio_empleo","tiempo_conseguir_empleo","factores_empleo",
        "labora_actualmente","tipo_institucion","sector_economico","tipo_contrato_actual",
        "actividades_empleo","escala_coincidencia","escala_conocimientos","escala_impacto",
        "escala_pertinencia","publicaciones","tipo_publicaciones","sni","red_tematica",
        "premios","descripcion_premios","academia","postdoctoral","escala_contenidos",
        "escala_didacticas","escala_evaluacion_doc","escala_biblio","escala_asesoria",
        "escala_satisfaccion","escala_laboratorios","escala_biblioteca","escala_internet",
        "escala_instalaciones","expectativas_cumplidas","calidad_programa","areas_mejora",
        "mejora_plan_estudios","cursos_actualizacion","descripcion_cursos",
        "actividades_deseadas","tiempo_disponible","empresa_propia","puesto_cinco_anos",
        "cargo_eleccion","descripcion_cargo","comentarios","recomendaria","fecha_encuesta"
    ]

    all_cols = ["user_id"] + COLS
    values   = [session.get("user_id")] + [serialize(d.get(col)) for col in COLS]
    placeholders = ",".join(["?"] * len(all_cols))
    cols_str = ",".join(all_cols)

    conn = get_db()
    c = conn.cursor()
    c.execute(f"INSERT INTO egresados ({cols_str}) VALUES ({placeholders})", values)
    conn.commit()
    new_id = c.lastrowid
    conn.close()

    return jsonify({"success": True, "id": new_id,
                    "message": "Cuestionario registrado exitosamente"})


@app.route("/api/egresados/<int:eid>", methods=["GET"])
@require_login
def get_egresado(eid):
    conn = get_db()
    c    = conn.cursor()
    c.execute("SELECT * FROM egresados WHERE id=?", (eid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"success": False, "error": "No encontrado"}), 404
    return jsonify({"success": True, "data": row_to_dict(row)})


# ──────────────────────────────────────────────────────────────────────────────
# API — Estadísticas (protegido)
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
@require_login
def get_stats():
    conn = get_db()
    c    = conn.cursor()
    s    = {}

    def scalar(q, p=()):
        c.execute(q, p)
        r = c.fetchone()
        return list(r)[0] if r else 0

    def rows(q, p=()):
        c.execute(q, p)
        return [dict(r) for r in c.fetchall()]

    s["total"]             = scalar("SELECT COUNT(*) FROM egresados")
    s["empleados"]         = scalar("SELECT COUNT(*) FROM egresados WHERE labora_actualmente='Sí'")
    s["sni_activos"]       = scalar("SELECT COUNT(*) FROM egresados WHERE sni LIKE '%actualmente%'")
    s["con_publicaciones"] = scalar("SELECT COUNT(*) FROM egresados WHERE publicaciones='Sí'")
    s["emprendedores"]     = scalar("SELECT COUNT(*) FROM egresados WHERE empresa_propia='Sí'")
    s["recomendarian"]     = scalar("SELECT COUNT(*) FROM egresados WHERE recomendaria LIKE 'Definitivamente sí%'")
    s["total_usuarios"]    = scalar("SELECT COUNT(*) FROM usuarios WHERE activo=1")

    s["por_programa"] = rows("""
        SELECT programa_posgrado AS label, COUNT(*) AS n
        FROM egresados WHERE programa_posgrado IS NOT NULL
        GROUP BY programa_posgrado ORDER BY n DESC
    """)
    s["por_sector"] = rows("""
        SELECT sector_economico AS label, COUNT(*) AS n
        FROM egresados WHERE sector_economico IS NOT NULL
        GROUP BY sector_economico ORDER BY n DESC
    """)
    s["por_calidad"] = rows("""
        SELECT calidad_programa AS label, COUNT(*) AS n
        FROM egresados WHERE calidad_programa IS NOT NULL
        GROUP BY calidad_programa ORDER BY n DESC
    """)
    s["satisfaccion_promedio"] = scalar("""
        SELECT ROUND(AVG(escala_satisfaccion),1)
        FROM egresados WHERE escala_satisfaccion IS NOT NULL
    """)

    conn.close()
    return jsonify({"success": True, "data": s})


# ──────────────────────────────────────────────────────────────────────────────
# Servir archivos estáticos
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:fname>")
def serve_static(fname):
    return send_from_directory(BASE_DIR, fname)


# ──────────────────────────────────────────────────────────────────────────────
# Inicio
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("\n" + "=" * 60)
    print("  ✅  Base de datos SQLite lista  →  egresados.db")
    print("  🔐  Admin por defecto  →  user: admin | pass: TecNM2025")
    print("  🚀  Portal corriendo en  →  http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000, host="0.0.0.0")
