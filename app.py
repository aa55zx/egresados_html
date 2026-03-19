"""
Portal de Egresados — TecNM Campus Oaxaca
Backend Flask + MySQL  (autenticación por token simple en header)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql, pymysql.cursors, os, json, functools, secrets
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
# Tokens activos: { token: {id, username, nombre, role} }
TOKENS = {}

app = Flask(__name__, static_folder=BASE_DIR)
CORS(app, supports_credentials=True)

# ──────────────────────────────────────────────────────────────────
# Configuración MySQL
# ──────────────────────────────────────────────────────────────────

MYSQL_CONFIG = {
    "host":        "localhost",
    "port":        3306,
    "user":        "root",
    "password":    "Ajas1500?",   # ← tu contraseña MySQL
    "database":    "egresados_tecnm",
    "charset":     "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit":  False,
}

def get_db():
    return pymysql.connect(**MYSQL_CONFIG)

def init_db():
    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id             INT AUTO_INCREMENT PRIMARY KEY,
                    username       VARCHAR(100) UNIQUE NOT NULL,
                    password_hash  VARCHAR(255) NOT NULL,
                    nombre         VARCHAR(255) NOT NULL,
                    email          VARCHAR(255),
                    role           VARCHAR(20) NOT NULL DEFAULT 'egresado',
                    activo         TINYINT(1) NOT NULL DEFAULT 1,
                    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS egresados (
                    id                       INT AUTO_INCREMENT PRIMARY KEY,
                    user_id                  INT,
                    nombre                   VARCHAR(255),
                    sexo                     VARCHAR(50),
                    estado_civil             VARCHAR(50),
                    municipio                VARCHAR(150),
                    ciudad                   VARCHAR(150),
                    codigo_postal            VARCHAR(10),
                    pais                     VARCHAR(100) DEFAULT 'México',
                    telefono                 VARCHAR(30),
                    email                    VARCHAR(255),
                    dependientes_economicos  VARCHAR(50),
                    razon_eleccion_ito       TEXT,
                    programa_posgrado        VARCHAR(255),
                    linea_investigacion      VARCHAR(255),
                    beca                     VARCHAR(10),
                    institucion_beca         VARCHAR(255),
                    tipo_beca                TEXT,
                    tiempo_extra_grado       VARCHAR(50),
                    causa_tiempo_extra       TEXT,
                    importancia_titulacion   VARCHAR(100),
                    dominio_idioma           VARCHAR(50),
                    idiomas                  VARCHAR(255),
                    certificacion_idioma     TEXT,
                    empleado_cursando        VARCHAR(10),
                    puesto_cursando          VARCHAR(255),
                    contrato_cursando        VARCHAR(100),
                    cambio_empleo            VARCHAR(10),
                    tiempo_conseguir_empleo  VARCHAR(100),
                    factores_empleo          TEXT,
                    labora_actualmente       VARCHAR(10),
                    tipo_institucion         VARCHAR(150),
                    sector_economico         VARCHAR(150),
                    tipo_contrato_actual     VARCHAR(100),
                    actividades_empleo       TEXT,
                    escala_coincidencia      TINYINT,
                    escala_conocimientos     TINYINT,
                    escala_impacto           TINYINT,
                    escala_pertinencia       TINYINT,
                    publicaciones            VARCHAR(10),
                    tipo_publicaciones       TEXT,
                    sni                      VARCHAR(100),
                    red_tematica             VARCHAR(255),
                    premios                  VARCHAR(10),
                    descripcion_premios      TEXT,
                    academia                 VARCHAR(10),
                    postdoctoral             TEXT,
                    escala_contenidos        TINYINT,
                    escala_didacticas        TINYINT,
                    escala_evaluacion_doc    TINYINT,
                    escala_biblio            TINYINT,
                    escala_asesoria          TINYINT,
                    escala_satisfaccion      TINYINT,
                    escala_laboratorios      TINYINT,
                    escala_biblioteca        TINYINT,
                    escala_internet          TINYINT,
                    escala_instalaciones     TINYINT,
                    expectativas_cumplidas   VARCHAR(50),
                    calidad_programa         VARCHAR(100),
                    areas_mejora             TEXT,
                    mejora_plan_estudios     TEXT,
                    cursos_actualizacion     VARCHAR(10),
                    descripcion_cursos       TEXT,
                    actividades_deseadas     TEXT,
                    tiempo_disponible        VARCHAR(100),
                    empresa_propia           VARCHAR(10),
                    puesto_cinco_anos        VARCHAR(255),
                    cargo_eleccion           VARCHAR(255),
                    descripcion_cargo        TEXT,
                    comentarios              TEXT,
                    recomendaria             VARCHAR(50),
                    fecha_encuesta           VARCHAR(50),
                    fecha_registro           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_egresado_usuario
                        FOREIGN KEY (user_id) REFERENCES usuarios(id)
                        ON DELETE SET NULL ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            conn.commit()
            c.execute("SELECT id FROM usuarios WHERE username='admin'")
            if not c.fetchone():
                c.execute("""
                    INSERT INTO usuarios (username, password_hash, nombre, role)
                    VALUES (%s, %s, %s, %s)
                """, ("admin", generate_password_hash("TecNM2025"),
                      "Administrador TecNM", "admin"))
                conn.commit()
                print("  👤  Admin creado  →  user: admin  |  pass: TecNM2025")
    finally:
        conn.close()

# ──────────────────────────────────────────────────────────────────
# Auth por token (header X-Auth-Token)
# ──────────────────────────────────────────────────────────────────

def get_current_user():
    token = request.headers.get("X-Auth-Token", "")
    return TOKENS.get(token)

def require_login(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not get_current_user():
            return jsonify({"success": False, "error": "No autenticado"}), 401
        return f(*args, **kwargs)
    return wrapper

def optional_login(f):
    """No requiere auth — pero si hay token, inyecta el usuario."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def require_admin(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "error": "No autenticado"}), 401
        if user["role"] != "admin":
            return jsonify({"success": False, "error": "Acceso denegado"}), 403
        return f(*args, **kwargs)
    return wrapper

# ──────────────────────────────────────────────────────────────────
# API — Autenticación
# ──────────────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    d        = request.get_json(silent=True) or {}
    username = (d.get("username") or "").strip()
    password = d.get("password") or ""

    if not username or not password:
        return jsonify({"success": False, "error": "Usuario y contraseña requeridos"}), 400

    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM usuarios WHERE username=%s AND activo=1", (username,))
            user = c.fetchone()
    finally:
        conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401

    token = secrets.token_hex(32)
    TOKENS[token] = {
        "id":       user["id"],
        "username": user["username"],
        "nombre":   user["nombre"],
        "role":     user["role"],
    }

    return jsonify({
        "success": True,
        "token": token,
        "user": TOKENS[token]
    })


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    token = request.headers.get("X-Auth-Token", "")
    TOKENS.pop(token, None)
    return jsonify({"success": True, "message": "Sesión cerrada"})


@app.route("/api/auth/me", methods=["GET"])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "authenticated": False}), 401
    return jsonify({"success": True, "authenticated": True, "user": user})

# ──────────────────────────────────────────────────────────────────
# API — Usuarios (solo admin)
# ──────────────────────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
@require_admin
def list_users():
    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute("SELECT id, username, nombre, email, role, activo, created_at FROM usuarios ORDER BY created_at DESC")
            users = c.fetchall()
    finally:
        conn.close()
    return jsonify({"success": True, "data": users, "total": len(users)})


@app.route("/api/users", methods=["POST"])
@require_admin
def create_user():
    d        = request.get_json(silent=True) or {}
    username = (d.get("username") or "").strip()
    password = d.get("password") or ""
    nombre   = (d.get("nombre") or "").strip()
    email    = (d.get("email") or "").strip()
    role     = d.get("role", "egresado")

    if not username or not password or not nombre:
        return jsonify({"success": False, "error": "username, password y nombre son requeridos"}), 400
    if role not in ("admin", "egresado"):
        return jsonify({"success": False, "error": "role inválido"}), 400

    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute("SELECT id FROM usuarios WHERE username=%s", (username,))
            if c.fetchone():
                return jsonify({"success": False, "error": "El usuario ya existe"}), 409
            c.execute("""
                INSERT INTO usuarios (username, password_hash, nombre, email, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, generate_password_hash(password), nombre, email, role))
            conn.commit()
            new_id = c.lastrowid
    finally:
        conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Usuario creado exitosamente"})


@app.route("/api/users/<int:uid>", methods=["GET"])
@require_admin
def get_user(uid):
    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute("SELECT id, username, nombre, email, role, activo, created_at FROM usuarios WHERE id=%s", (uid,))
            row = c.fetchone()
    finally:
        conn.close()
    if not row:
        return jsonify({"success": False, "error": "No encontrado"}), 404
    return jsonify({"success": True, "data": row})


@app.route("/api/users/<int:uid>", methods=["PUT"])
@require_admin
def update_user(uid):
    d = request.get_json(silent=True) or {}
    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM usuarios WHERE id=%s", (uid,))
            user = c.fetchone()
            if not user:
                return jsonify({"success": False, "error": "No encontrado"}), 404

            nombre = d.get("nombre", user["nombre"])
            email  = d.get("email",  user["email"])
            role   = d.get("role",   user["role"])
            activo = d.get("activo", user["activo"])

            updates = ["nombre=%s", "email=%s", "role=%s", "activo=%s"]
            values  = [nombre, email, role, activo]

            if d.get("password"):
                updates.append("password_hash=%s")
                values.append(generate_password_hash(d["password"]))

            values.append(uid)
            c.execute(f"UPDATE usuarios SET {', '.join(updates)} WHERE id=%s", values)
            conn.commit()
    finally:
        conn.close()
    return jsonify({"success": True, "message": "Usuario actualizado"})


@app.route("/api/users/<int:uid>", methods=["DELETE"])
@require_admin
def delete_user(uid):
    current = get_current_user()
    if current and current["id"] == uid:
        return jsonify({"success": False, "error": "No puedes eliminar tu propia cuenta"}), 400
    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute("SELECT id FROM usuarios WHERE id=%s", (uid,))
            if not c.fetchone():
                return jsonify({"success": False, "error": "No encontrado"}), 404
            c.execute("DELETE FROM usuarios WHERE id=%s", (uid,))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"success": True, "message": "Usuario eliminado"})

# ──────────────────────────────────────────────────────────────────
# Helpers egresados
# ──────────────────────────────────────────────────────────────────

JSON_FIELDS = {"razon_eleccion_ito","tipo_beca","certificacion_idioma","factores_empleo","tipo_publicaciones"}

def row_to_dict(row):
    d = dict(row)
    for f in JSON_FIELDS:
        if d.get(f):
            try: d[f] = json.loads(d[f])
            except: pass
    return d

def serialize(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v

# ──────────────────────────────────────────────────────────────────
# API — Egresados
# ──────────────────────────────────────────────────────────────────

@app.route("/api/egresados", methods=["GET"])
def list_egresados():
    search = request.args.get("search","").strip()
    prog   = request.args.get("programa","").strip()
    sector = request.args.get("sector","").strip()
    sni_f  = request.args.get("sni","").strip()
    page   = max(1, int(request.args.get("page",1)))
    per    = min(50, int(request.args.get("per",12)))

    where, params = ["1=1"], []
    if search:
        where.append("(nombre LIKE %s OR email LIKE %s OR ciudad LIKE %s OR programa_posgrado LIKE %s)")
        params += [f"%{search}%"]*4
    if prog:
        where.append("programa_posgrado LIKE %s"); params.append(f"%{prog}%")
    if sector:
        where.append("sector_economico LIKE %s"); params.append(f"%{sector}%")
    if sni_f:
        where.append("sni LIKE %s"); params.append(f"%{sni_f}%")

    base_q = f"FROM egresados WHERE {' AND '.join(where)}"
    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute(f"SELECT COUNT(*) AS n {base_q}", params)
            total = c.fetchone()["n"]
            c.execute(f"SELECT * {base_q} ORDER BY fecha_registro DESC LIMIT %s OFFSET %s",
                      params + [per, (page-1)*per])
            rows = [row_to_dict(r) for r in c.fetchall()]
    finally:
        conn.close()
    return jsonify({"success":True,"data":rows,"total":total,"page":page,"per":per,"pages":max(1,-(-total//per))})


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
    user     = get_current_user()
    all_cols = ["user_id"] + COLS
    values   = [user["id"] if user else None] + [serialize(d.get(col)) for col in COLS]
    cols_str = ",".join(f"`{c}`" for c in all_cols)
    placeholders = ",".join(["%s"]*len(all_cols))

    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute(f"INSERT INTO egresados ({cols_str}) VALUES ({placeholders})", values)
            conn.commit()
            new_id = c.lastrowid
    finally:
        conn.close()
    return jsonify({"success": True, "id": new_id, "message": "Cuestionario registrado exitosamente"})


@app.route("/api/egresados/<int:eid>", methods=["GET"])
def get_egresado(eid):
    conn = get_db()
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM egresados WHERE id=%s", (eid,))
            row = c.fetchone()
    finally:
        conn.close()
    if not row:
        return jsonify({"success": False, "error": "No encontrado"}), 404
    return jsonify({"success": True, "data": row_to_dict(row)})

# ──────────────────────────────────────────────────────────────────
# API — Estadísticas
# ──────────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    s = {}
    try:
        with conn.cursor() as c:
            def scalar(q, p=()):
                c.execute(q, p); r = c.fetchone()
                return list(r.values())[0] if r else 0
            def rows(q, p=()):
                c.execute(q, p); return c.fetchall()

            s["total"]             = scalar("SELECT COUNT(*) FROM egresados")
            s["empleados"]         = scalar("SELECT COUNT(*) FROM egresados WHERE labora_actualmente='Sí'")
            s["sni_activos"]       = scalar("SELECT COUNT(*) FROM egresados WHERE sni LIKE '%actualmente%'")
            s["con_publicaciones"] = scalar("SELECT COUNT(*) FROM egresados WHERE publicaciones='Sí'")
            s["emprendedores"]     = scalar("SELECT COUNT(*) FROM egresados WHERE empresa_propia='Sí'")
            s["recomendarian"]     = scalar("SELECT COUNT(*) FROM egresados WHERE recomendaria LIKE 'Definitivamente sí%'")
            s["total_usuarios"]    = scalar("SELECT COUNT(*) FROM usuarios WHERE activo=1")
            s["por_programa"]      = rows("SELECT programa_posgrado AS label, COUNT(*) AS n FROM egresados WHERE programa_posgrado IS NOT NULL GROUP BY programa_posgrado ORDER BY n DESC")
            s["por_sector"]        = rows("SELECT sector_economico AS label, COUNT(*) AS n FROM egresados WHERE sector_economico IS NOT NULL GROUP BY sector_economico ORDER BY n DESC")
            s["por_calidad"]       = rows("SELECT calidad_programa AS label, COUNT(*) AS n FROM egresados WHERE calidad_programa IS NOT NULL GROUP BY calidad_programa ORDER BY n DESC")
            s["satisfaccion_promedio"] = scalar("SELECT ROUND(AVG(escala_satisfaccion),1) FROM egresados WHERE escala_satisfaccion IS NOT NULL")
    finally:
        conn.close()
    return jsonify({"success": True, "data": s})

# ──────────────────────────────────────────────────────────────────
# Archivos estáticos
# ──────────────────────────────────────────────────────────────────

@app.route("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:fname>")
def serve_static(fname):
    return send_from_directory(BASE_DIR, fname)

# ──────────────────────────────────────────────────────────────────
# Inicio
# ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("\n" + "="*60)
    print("  ✅  Base de datos MySQL lista  →  egresados_tecnm")
    print("  🔐  Admin  →  user: admin | pass: TecNM2025")
    print("  🚀  Portal  →  http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, host="0.0.0.0")
