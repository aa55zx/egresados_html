-- =====================================================================
--  SUPABASE_FIXES.SQL
--  Ejecuta esto en: Supabase Dashboard -> SQL Editor
--  Proyecto: Portal de Egresados TecNM Campus Oaxaca (Modo Serverless)
-- =====================================================================

-- 1. Permitir que password_hash sea opcional (nulo), ya que Supabase Auth maneja las contraseñas
ALTER TABLE usuarios ALTER COLUMN password_hash DROP NOT NULL;


-- 2. Vincular cuentas de prueba existentes con sus UUIDs de Supabase Auth
--
-- INSTRUCCIONES:
--   a) Ve a Supabase Dashboard -> Authentication -> Users.
--   b) Agrega las cuentas con sus correos y contraseñas reales.
--   c) Copia el UUID generado para cada uno.
--   d) Reemplaza los UUIDs en las siguientes líneas y ejecútalas:

UPDATE usuarios 
SET auth_id = 'PEGA_AQUI_EL_UUID_DE_ADMIN',
    email = 'admin.posgrado@itoaxaca.edu.mx'
WHERE username = 'admin';

UPDATE usuarios 
SET auth_id = 'PEGA_AQUI_EL_UUID_DE_EGRESADO',
    email = 'egresado@itoaxaca.edu.mx'
WHERE username = 'egresado';

UPDATE usuarios 
SET auth_id = 'PEGA_AQUI_EL_UUID_DE_EMPRESA',
    email = 'contacto@techsolutions.com'
WHERE username = 'empresa';


-- 3. Verificar que quedaron correctos
SELECT id, username, nombre, email, role, activo, auth_id, password_hash FROM usuarios;
