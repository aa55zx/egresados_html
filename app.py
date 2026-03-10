"""
Portal de Egresados — TecNM Campus Oaxaca
Backend Flask + SQLite
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os, json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "egresados.db")

app = Flask(__name__, static_folder=BASE_DIR)
CORS(app)

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
    c.execute("""
        CREATE TABLE IF NOT EXISTS egresados (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
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
            razon_eleccion_ito      TEXT,   -- JSON array
            programa_posgrado       TEXT,
            linea_investigacion     TEXT,
            beca                    TEXT,
            institucion_beca        TEXT,
            tipo_beca               TEXT,   -- JSON array
            tiempo_extra_grado      TEXT,
            causa_tiempo_extra      TEXT,
            importancia_titulacion  TEXT,
            dominio_idioma          TEXT,
            idiomas                 TEXT,
            certificacion_idioma    TEXT,   -- JSON array
            -- ── Sección III: Laboral ──
            empleado_cursando       TEXT,
            puesto_cursando         TEXT,
            contrato_cursando       TEXT,
            cambio_empleo           TEXT,
            tiempo_conseguir_empleo TEXT,
            factores_empleo         TEXT,   -- JSON array
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
            tipo_publicaciones      TEXT,   -- JSON array
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
# Helpers
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
# API — Egresados
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/egresados", methods=["GET"])
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
        "pages":   max(1, -(-total // per))   # ceil division
    })


@app.route("/api/egresados", methods=["POST"])
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

    values = [serialize(d.get(col)) for col in COLS]
    placeholders = ",".join(["?"] * len(COLS))
    cols_str = ",".join(COLS)

    conn = get_db()
    c = conn.cursor()
    c.execute(f"INSERT INTO egresados ({cols_str}) VALUES ({placeholders})", values)
    conn.commit()
    new_id = c.lastrowid
    conn.close()

    return jsonify({"success": True, "id": new_id,
                    "message": "Cuestionario registrado exitosamente"})


@app.route("/api/egresados/<int:eid>", methods=["GET"])
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
# API — Estadísticas para reportes
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
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

    s["total"]            = scalar("SELECT COUNT(*) FROM egresados")
    s["empleados"]        = scalar("SELECT COUNT(*) FROM egresados WHERE labora_actualmente='Sí'")
    s["sni_activos"]      = scalar("SELECT COUNT(*) FROM egresados WHERE sni LIKE '%actualmente%'")
    s["con_publicaciones"]= scalar("SELECT COUNT(*) FROM egresados WHERE publicaciones='Sí'")
    s["emprendedores"]    = scalar("SELECT COUNT(*) FROM egresados WHERE empresa_propia='Sí'")
    s["recomendarian"]    = scalar("SELECT COUNT(*) FROM egresados WHERE recomendaria LIKE 'Definitivamente sí%'")

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
    s["por_tiempo_empleo"] = rows("""
        SELECT tiempo_conseguir_empleo AS label, COUNT(*) AS n
        FROM egresados WHERE tiempo_conseguir_empleo IS NOT NULL
        GROUP BY tiempo_conseguir_empleo ORDER BY n DESC
    """)
    s["satisfaccion_promedio"] = scalar("""
        SELECT ROUND(AVG(escala_satisfaccion),1)
        FROM egresados WHERE escala_satisfaccion IS NOT NULL
    """)

    conn.close()
    return jsonify({"success": True, "data": s})


# ──────────────────────────────────────────────────────────────────────────────
# Servir archivos estáticos (HTML, CSS, JS, imágenes)
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
    print("\n" + "=" * 55)
    print("  ✅  Base de datos SQLite lista  →  egresados.db")
    print("  🚀  Portal corriendo en  →  http://localhost:5000")
    print("=" * 55 + "\n")
    app.run(debug=True, port=5000, host="0.0.0.0")
