-- ============================================================
--  supabase_setup.sql
--  Ejecuta esto en: Supabase Dashboard → SQL Editor
--  Proyecto: Portal de Egresados TecNM Campus Oaxaca
-- ============================================================

-- 1. Agregar columna auth_id a la tabla usuarios
--    (vincula cada usuario con su cuenta en Supabase Auth)
ALTER TABLE usuarios
  ADD COLUMN IF NOT EXISTS auth_id UUID UNIQUE;

-- 2. Habilitar Row Level Security (RLS) en las tablas
ALTER TABLE usuarios    ENABLE ROW LEVEL SECURITY;
ALTER TABLE egresados   ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizaciones ENABLE ROW LEVEL SECURITY;

-- 3. Políticas para tabla usuarios
--    Admin puede ver y modificar todo
--    Usuarios autenticados pueden ver su propio perfil

DROP POLICY IF EXISTS "usuarios_select_own"  ON usuarios;
DROP POLICY IF EXISTS "usuarios_select_admin" ON usuarios;
DROP POLICY IF EXISTS "usuarios_insert_admin" ON usuarios;
DROP POLICY IF EXISTS "usuarios_update_admin" ON usuarios;
DROP POLICY IF EXISTS "usuarios_delete_admin" ON usuarios;

-- Cualquier usuario autenticado puede leer su propio perfil
CREATE POLICY "usuarios_select_own" ON usuarios
  FOR SELECT USING (auth.uid() = auth_id);

-- Admin puede leer todos los usuarios
CREATE POLICY "usuarios_select_admin" ON usuarios
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM usuarios u
      WHERE u.auth_id = auth.uid() AND u.role = 'admin'
    )
  );

-- Admin puede crear usuarios
CREATE POLICY "usuarios_insert_admin" ON usuarios
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios u
      WHERE u.auth_id = auth.uid() AND u.role = 'admin'
    )
  );

-- Admin puede actualizar usuarios
CREATE POLICY "usuarios_update_admin" ON usuarios
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM usuarios u
      WHERE u.auth_id = auth.uid() AND u.role = 'admin'
    )
  );

-- Admin puede eliminar usuarios
CREATE POLICY "usuarios_delete_admin" ON usuarios
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM usuarios u
      WHERE u.auth_id = auth.uid() AND u.role = 'admin'
    )
  );

-- 4. Políticas para tabla egresados
DROP POLICY IF EXISTS "egresados_select_all"    ON egresados;
DROP POLICY IF EXISTS "egresados_insert_auth"   ON egresados;
DROP POLICY IF EXISTS "egresados_update_own"    ON egresados;

-- Cualquiera puede leer egresados (directorio público)
CREATE POLICY "egresados_select_all" ON egresados
  FOR SELECT USING (true);

-- Solo usuarios autenticados pueden insertar
CREATE POLICY "egresados_insert_auth" ON egresados
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Admin puede actualizar cualquier egresado
CREATE POLICY "egresados_update_own" ON egresados
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM usuarios u
      WHERE u.auth_id = auth.uid() AND u.role = 'admin'
    )
  );

-- 5. Políticas para tabla organizaciones
DROP POLICY IF EXISTS "org_select_admin"  ON organizaciones;
DROP POLICY IF EXISTS "org_insert_auth"   ON organizaciones;

CREATE POLICY "org_select_admin" ON organizaciones
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM usuarios u
      WHERE u.auth_id = auth.uid() AND u.role IN ('admin', 'organizacion')
    )
  );

CREATE POLICY "org_insert_auth" ON organizaciones
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- ============================================================
-- INSTRUCCIONES PARA CREAR EL USUARIO ADMIN:
--
-- 1. Ve a: Supabase Dashboard → Authentication → Users
-- 2. Haz clic en "Add user" → "Create new user"
-- 3. Email:    admin@tecnm-oaxaca.edu.mx
-- 4. Password: TecNM2025!
-- 5. Haz clic en "Create User"
-- 6. Copia el UUID del usuario creado
-- 7. Ejecuta el siguiente INSERT reemplazando el UUID:
-- ============================================================

-- PASO FINAL: vincular el admin de Auth con la tabla usuarios
-- Reemplaza 'PEGA-AQUI-EL-UUID-DE-SUPABASE-AUTH' con el UUID real
UPDATE usuarios
SET auth_id = 'PEGA-AQUI-EL-UUID-DE-SUPABASE-AUTH',
    email   = 'admin@tecnm-oaxaca.edu.mx'
WHERE username = 'admin' AND role = 'admin';

-- Verificar que quedó correcto:
SELECT id, username, nombre, role, activo, auth_id FROM usuarios;
