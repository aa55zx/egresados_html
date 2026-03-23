-- ============================================================
--  Script de creación de base de datos
--  Proyecto: Portal de Egresados — TecNM Campus Oaxaca
--  Motor:    MySQL 8.x  (compatible con MySQL Workbench)
--  Ejecución: Abre este archivo en Workbench y presiona ⚡
-- ============================================================

-- 1. Crear y seleccionar la base de datos
CREATE DATABASE IF NOT EXISTS egresados_tecnm
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE egresados_tecnm;

-- ============================================================
-- 2. Tabla: usuarios
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(100)  UNIQUE NOT NULL,
    password_hash  VARCHAR(255)  NOT NULL,
    nombre         VARCHAR(255)  NOT NULL,
    email          VARCHAR(255),
    role           VARCHAR(20)   NOT NULL DEFAULT 'egresado'
                   COMMENT 'Valores: admin | egresado | organizacion',
    activo         TINYINT(1)    NOT NULL DEFAULT 1,
    created_at     TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 3. Tabla: egresados
-- ============================================================
CREATE TABLE IF NOT EXISTS egresados (
    id                       INT AUTO_INCREMENT PRIMARY KEY,
    user_id                  INT,

    -- Datos personales
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

    -- Formación y posgrado
    razon_eleccion_ito       TEXT        COMMENT 'JSON array',
    programa_posgrado        VARCHAR(255),
    linea_investigacion      VARCHAR(255),
    beca                     VARCHAR(10),
    institucion_beca         VARCHAR(255),
    tipo_beca                TEXT        COMMENT 'JSON array',
    tiempo_extra_grado       VARCHAR(50),
    causa_tiempo_extra       TEXT,
    importancia_titulacion   VARCHAR(100),

    -- Idiomas
    dominio_idioma           VARCHAR(50),
    idiomas                  VARCHAR(255),
    certificacion_idioma     TEXT        COMMENT 'JSON array',

    -- Situación laboral durante el posgrado
    empleado_cursando        VARCHAR(10),
    puesto_cursando          VARCHAR(255),
    contrato_cursando        VARCHAR(100),
    cambio_empleo            VARCHAR(10),
    tiempo_conseguir_empleo  VARCHAR(100),
    factores_empleo          TEXT        COMMENT 'JSON array',

    -- Situación laboral actual
    labora_actualmente       VARCHAR(10),
    tipo_institucion         VARCHAR(150),
    sector_economico         VARCHAR(150),
    tipo_contrato_actual     VARCHAR(100),
    actividades_empleo       TEXT,

    -- Escalas de valoración (1-5)
    escala_coincidencia      TINYINT,
    escala_conocimientos     TINYINT,
    escala_impacto           TINYINT,
    escala_pertinencia       TINYINT,

    -- Producción académica
    publicaciones            VARCHAR(10),
    tipo_publicaciones       TEXT        COMMENT 'JSON array',
    sni                      VARCHAR(100),
    red_tematica             VARCHAR(255),
    premios                  VARCHAR(10),
    descripcion_premios      TEXT,
    academia                 VARCHAR(10),
    postdoctoral             TEXT,

    -- Evaluación del programa
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

    -- Opinión sobre el programa
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

    -- Metadatos
    fecha_registro           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_egresado_usuario
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
        ON DELETE SET NULL ON UPDATE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 4. Tabla: organizaciones
-- ============================================================
CREATE TABLE IF NOT EXISTS organizaciones (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    user_id                 INT,

    -- Datos generales
    fecha                   VARCHAR(20),
    nombre_empresa          VARCHAR(255),
    direccion               TEXT,
    municipio_estado        VARCHAR(255),
    codigo_postal           VARCHAR(10),
    cargo_persona           VARCHAR(255),
    area_adscripcion        VARCHAR(255),
    correo                  VARCHAR(255),
    telefono                VARCHAR(30),

    -- Tipo y tamaño
    tipo_empresa            VARCHAR(100),
    tipo_empresa_otro       VARCHAR(255),
    tamano_empresa          VARCHAR(100),
    sector                  VARCHAR(255),
    sector_otro             VARCHAR(255),

    -- Contratación de posgrado
    posgrado_maestria       VARCHAR(50),
    posgrado_doctorado      VARCHAR(50),
    posgrado_posdoctorado   VARCHAR(50),
    caract_contratacion     TEXT,
    perfiles_requeridos     TEXT,
    perfiles_ingenieria     TEXT,
    perfiles_otro           VARCHAR(255),
    seleccion_personal      TEXT,
    habilidades_campo       TEXT,
    competencias_generales  TEXT,

    -- Vinculación
    vinculacion_activa      VARCHAR(10),
    vinculacion_tipos       TEXT,
    vinculacion_otro        VARCHAR(255),

    -- Estudiantes
    estudiantes_posgrado    VARCHAR(10),
    estudiantes_tipo        VARCHAR(255),
    estudiantes_cantidad    VARCHAR(50),
    estudiantes_no_razon    TEXT,

    -- Prospectiva
    areas_oportunidad       TEXT,
    nuevos_perfiles         TEXT,
    problematica            TEXT,
    tematicas_oportunidad   TEXT,
    fortalezas              TEXT,
    areas_atencion          TEXT,
    comentarios_generales   TEXT,

    -- Metadatos
    fecha_registro          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_org_usuario
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
        ON DELETE SET NULL ON UPDATE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 5. Usuario administrador por defecto
--    Contraseña: TecNM2025  (hash bcrypt generado por Flask)
--    ⚠️  Cámbiala después del primer login
-- ============================================================
INSERT IGNORE INTO usuarios (username, password_hash, nombre, role)
VALUES (
    'admin',
    'pbkdf2:sha256:1000000$placeholder$changeme',  -- Flask sobreescribe esto en init_db()
    'Administrador TecNM',
    'admin'
);

-- ============================================================
-- 6. Verificación rápida
-- ============================================================
SELECT 'Tablas creadas correctamente:' AS mensaje;
SHOW TABLES;
