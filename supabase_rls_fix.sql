-- =====================================================================
--  SUPABASE_RLS_FIX.SQL
--  Ejecuta esto en: Supabase Dashboard -> SQL Editor
--  Proyecto: Portal de Egresados TecNM Campus Oaxaca
--  Propósito: Resolver el error de recursión infinita en las políticas RLS
--             que impedía el inicio de sesión de los usuarios.
-- =====================================================================

-- 1. Crear funciones de ayuda con contexto SECURITY DEFINER
--    (Permiten realizar consultas internas en la tabla 'usuarios' saltándose RLS para evitar recursión)

CREATE OR REPLACE FUNCTION public.es_admin()
RETURNS boolean
SECURITY DEFINER
SET search_path = public
LANGUAGE sql
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.usuarios
    WHERE auth_id = auth.uid() AND role = 'admin'
  );
$$;

CREATE OR REPLACE FUNCTION public.tiene_rol(roles_requeridos text[])
RETURNS boolean
SECURITY DEFINER
SET search_path = public
LANGUAGE sql
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.usuarios
    WHERE auth_id = auth.uid() AND role = ANY(roles_requeridos)
  );
$$;

CREATE OR REPLACE FUNCTION public.get_current_usuario_id()
RETURNS integer
SECURITY DEFINER
SET search_path = public
LANGUAGE sql
AS $$
  SELECT id FROM public.usuarios
  WHERE auth_id = auth.uid()
  LIMIT 1;
$$;


-- 2. Limpiar y recrear las políticas de la tabla 'usuarios'

DROP POLICY IF EXISTS "usuarios: admin actualiza" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios: admin elimina" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios: admin inserta" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios: admin lee todos" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios: leer perfil propio" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_delete_admin" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_insert_admin" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_select_admin" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_select_own" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_update_admin" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_select_policy" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_insert_policy" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_update_policy" ON public.usuarios;
DROP POLICY IF EXISTS "usuarios_delete_policy" ON public.usuarios;

ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "usuarios_select_policy" ON public.usuarios
  FOR SELECT USING (auth.uid() = auth_id OR public.es_admin());

CREATE POLICY "usuarios_insert_policy" ON public.usuarios
  FOR INSERT WITH CHECK (public.es_admin());

CREATE POLICY "usuarios_update_policy" ON public.usuarios
  FOR UPDATE USING (auth.uid() = auth_id OR public.es_admin());

CREATE POLICY "usuarios_delete_policy" ON public.usuarios
  FOR DELETE USING (public.es_admin());


-- 3. Limpiar y recrear las políticas de la tabla 'egresados'

DROP POLICY IF EXISTS "egresados: actualizar propio o admin" ON public.egresados;
DROP POLICY IF EXISTS "egresados: insertar autenticado" ON public.egresados;
DROP POLICY IF EXISTS "egresados: lectura publica" ON public.egresados;
DROP POLICY IF EXISTS "egresados_insert_auth" ON public.egresados;
DROP POLICY IF EXISTS "egresados_select_all" ON public.egresados;
DROP POLICY IF EXISTS "egresados_update_own" ON public.egresados;
DROP POLICY IF EXISTS "egresados_select_policy" ON public.egresados;
DROP POLICY IF EXISTS "egresados_insert_policy" ON public.egresados;
DROP POLICY IF EXISTS "egresados_update_policy" ON public.egresados;
DROP POLICY IF EXISTS "egresados_delete_policy" ON public.egresados;

ALTER TABLE public.egresados ENABLE ROW LEVEL SECURITY;

CREATE POLICY "egresados_select_policy" ON public.egresados
  FOR SELECT USING (true);

CREATE POLICY "egresados_insert_policy" ON public.egresados
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL AND (user_id = public.get_current_usuario_id() OR public.es_admin()));

CREATE POLICY "egresados_update_policy" ON public.egresados
  FOR UPDATE USING (user_id = public.get_current_usuario_id() OR public.es_admin());

CREATE POLICY "egresados_delete_policy" ON public.egresados
  FOR DELETE USING (public.es_admin());


-- 4. Limpiar y recrear las políticas de la tabla 'organizaciones'

DROP POLICY IF EXISTS "org_insert_auth" ON public.organizaciones;
DROP POLICY IF EXISTS "org_select_admin" ON public.organizaciones;
DROP POLICY IF EXISTS "organizaciones: admin lee todas" ON public.organizaciones;
DROP POLICY IF EXISTS "organizaciones: insertar autenticado" ON public.organizaciones;
DROP POLICY IF EXISTS "organizaciones: leer propio" ON public.organizaciones;
DROP POLICY IF EXISTS "organizaciones_select_policy" ON public.organizaciones;
DROP POLICY IF EXISTS "organizaciones_insert_policy" ON public.organizaciones;
DROP POLICY IF EXISTS "organizaciones_update_policy" ON public.organizaciones;
DROP POLICY IF EXISTS "organizaciones_delete_policy" ON public.organizaciones;

ALTER TABLE public.organizaciones ENABLE ROW LEVEL SECURITY;

CREATE POLICY "organizaciones_select_policy" ON public.organizaciones
  FOR SELECT USING (public.tiene_rol(ARRAY['admin', 'organizacion']) OR user_id = public.get_current_usuario_id());

CREATE POLICY "organizaciones_insert_policy" ON public.organizaciones
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL AND (user_id = public.get_current_usuario_id() OR public.es_admin()));

CREATE POLICY "organizaciones_update_policy" ON public.organizaciones
  FOR UPDATE USING (user_id = public.get_current_usuario_id() OR public.es_admin());

CREATE POLICY "organizaciones_delete_policy" ON public.organizaciones
  FOR DELETE USING (public.es_admin());
