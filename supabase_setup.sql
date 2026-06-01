-- ================================================================
-- SETUP SUPABASE: Portal de Egresados TecNM
-- Ejecutar en: Supabase Dashboard → SQL Editor
-- ================================================================

-- 1. Agregar columna user_id a usuarios para vincular con Supabase Auth
ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- ----------------------------------------------------------------
-- 2. HABILITAR RLS en todas las tablas
-- ----------------------------------------------------------------
ALTER TABLE usuarios      ENABLE ROW LEVEL SECURITY;
ALTER TABLE egresados     ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizaciones ENABLE ROW LEVEL SECURITY;

-- ----------------------------------------------------------------
-- 3. POLÍTICAS para tabla: usuarios
-- ----------------------------------------------------------------

-- Cualquier usuario autenticado puede leer su propio perfil
CREATE POLICY "usuarios: leer perfil propio"
ON usuarios FOR SELECT
USING (auth.uid() = user_id);

-- Los admins pueden leer todos los perfiles
CREATE POLICY "usuarios: admin lee todos"
ON usuarios FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios u
        WHERE u.user_id = auth.uid() AND u.role = 'admin'
    )
);

-- Los admins pueden actualizar cualquier perfil
CREATE POLICY "usuarios: admin actualiza"
ON usuarios FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM usuarios u
        WHERE u.user_id = auth.uid() AND u.role = 'admin'
    )
);

-- Los admins pueden insertar usuarios
CREATE POLICY "usuarios: admin inserta"
ON usuarios FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM usuarios u
        WHERE u.user_id = auth.uid() AND u.role = 'admin'
    )
);

-- Los admins pueden eliminar usuarios (excepto a sí mismos)
CREATE POLICY "usuarios: admin elimina"
ON usuarios FOR DELETE
USING (
    EXISTS (
        SELECT 1 FROM usuarios u
        WHERE u.user_id = auth.uid() AND u.role = 'admin'
    )
);

-- ----------------------------------------------------------------
-- 4. POLÍTICAS para tabla: egresados
-- ----------------------------------------------------------------

-- Lectura pública (directorio de egresados es visible para todos)
CREATE POLICY "egresados: lectura publica"
ON egresados FOR SELECT
USING (true);

-- Solo el egresado dueño puede insertar su encuesta
CREATE POLICY "egresados: insertar autenticado"
ON egresados FOR INSERT
WITH CHECK (
    auth.uid() IS NOT NULL AND (
        user_id IS NULL OR
        user_id = (SELECT id FROM usuarios WHERE user_id = auth.uid() LIMIT 1)
    )
);

-- El egresado puede actualizar su propio registro; admin puede actualizar cualquiera
CREATE POLICY "egresados: actualizar propio o admin"
ON egresados FOR UPDATE
USING (
    user_id = (SELECT id FROM usuarios WHERE user_id = auth.uid() LIMIT 1)
    OR EXISTS (
        SELECT 1 FROM usuarios u WHERE u.user_id = auth.uid() AND u.role = 'admin'
    )
);

-- ----------------------------------------------------------------
-- 5. POLÍTICAS para tabla: organizaciones
-- ----------------------------------------------------------------

-- Solo el usuario autenticado puede insertar su encuesta
CREATE POLICY "organizaciones: insertar autenticado"
ON organizaciones FOR INSERT
WITH CHECK (auth.uid() IS NOT NULL);

-- Los admins pueden leer todas las organizaciones
CREATE POLICY "organizaciones: admin lee todas"
ON organizaciones FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM usuarios u WHERE u.user_id = auth.uid() AND u.role = 'admin'
    )
);

-- La organización dueña puede leer su propio registro
CREATE POLICY "organizaciones: leer propio"
ON organizaciones FOR SELECT
USING (
    user_id = (SELECT id FROM usuarios WHERE user_id = auth.uid() LIMIT 1)
);

-- ----------------------------------------------------------------
-- 6. FUNCIÓN + TRIGGER: crear perfil automáticamente al registrarse
-- ----------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Solo actualiza user_id si existe un registro con el mismo email
    UPDATE public.usuarios
    SET user_id = NEW.id
    WHERE email = NEW.email AND user_id IS NULL;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger que se ejecuta cuando se crea un nuevo usuario en Auth
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ----------------------------------------------------------------
-- 7. VINCULAR usuarios existentes (si ya tienen email en la tabla)
--    Ejecuta esto DESPUÉS de crear los usuarios en Supabase Auth
-- ----------------------------------------------------------------
-- UPDATE public.usuarios u
-- SET user_id = a.id
-- FROM auth.users a
-- WHERE a.email = u.email AND u.user_id IS NULL;
