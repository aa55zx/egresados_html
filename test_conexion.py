import psycopg2
import socket

password = "3G456G65H 6H"
ref = "lgmckhssohxdqmhszgtn"

# Supabase tiene poolers en distintas regiones
regiones = [
    "aws-0-us-east-1",
    "aws-0-us-west-1",
    "aws-0-us-east-2",
    "aws-0-eu-central-1",
    "aws-0-eu-west-1",
    "aws-0-eu-west-2",
    "aws-0-ap-southeast-1",
    "aws-0-ap-northeast-1",
    "aws-0-ap-southeast-2",
    "aws-0-sa-east-1",
    "aws-0-ca-central-1",
]

print(f"Buscando region correcta para proyecto: {ref}")
print("="*55)

exitosa = None
for region in regiones:
    host = f"{region}.pooler.supabase.com"
    print(f"\nProbando region: {region}")

    # Primero verificar si el host resuelve
    try:
        ip = socket.gethostbyname(host)
        print(f"  DNS OK -> {ip}")
    except:
        print(f"  DNS: no resuelve, saltando...")
        continue

    # Intentar conexion
    for port in [6543, 5432]:
        try:
            conn = psycopg2.connect(
                host=host, port=port,
                user=f"postgres.{ref}",
                password=password,
                dbname="postgres",
                connect_timeout=6
            )
            conn.cursor().execute("SELECT 1")
            conn.close()
            print(f"  >>> EXITOSA en puerto {port} <<<")
            exitosa = {"host": host, "port": port, "region": region}
            break
        except Exception as e:
            msg = str(e).split("\n")[0][:80]
            print(f"  Puerto {port}: {msg}")
    if exitosa:
        break

print("\n" + "="*55)
if exitosa:
    print(f"REGION CORRECTA: {exitosa['region']}")
    print(f"Host:  {exitosa['host']}")
    print(f"Port:  {exitosa['port']}")
    print("\nDATABASE_URL para .env:")
    print(f"postgresql://postgres.{ref}:{password}@{exitosa['host']}:{exitosa['port']}/postgres")
else:
    print("No se encontro ninguna region funcional.")
    print("")
    print("Solucion alternativa: cambia la contrasena en Supabase")
    print("Settings > Database > Reset database password")
    print("Usa una sin espacios, ejemplo: TecNM2025db")

input("\nPresiona Enter para cerrar...")
