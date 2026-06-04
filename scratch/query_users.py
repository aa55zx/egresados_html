import psycopg2
import psycopg2.extras

def test_query():
    host = "aws-1-us-east-1.pooler.supabase.com"
    port = 6543
    user = "postgres.lgmckhssohxdqmhszgtn"
    pwd = "3G456G65H6H"
    
    try:
        conn = psycopg2.connect(
            host=host, port=port,
            dbname="postgres", user=user,
            password=pwd, sslmode="require",
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        print("Successfully connected to Supabase database.")
        with conn.cursor() as cur:
            # Check if usuarios table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'usuarios'
                );
            """)
            exists = cur.fetchone()['exists']
            print(f"Table 'usuarios' exists: {exists}")
            
            if exists:
                cur.execute("SELECT id, username, nombre, email, role, activo, auth_id FROM usuarios;")
                rows = cur.fetchall()
                print(f"Total users found: {len(rows)}")
                for r in rows:
                    print(f"  - User: {r['username']} (ID: {r['id']})")
                    print(f"    Name: {r['nombre']}")
                    print(f"    Email: {r['email']}")
                    print(f"    Role: {r['role']}")
                    print(f"    Active: {r['activo']}")
                    print(f"    Auth ID (UUID): {r['auth_id']}")
            else:
                print("No usuarios table found.")
        conn.close()
    except Exception as e:
        print(f"Database query failed: {e}")

if __name__ == "__main__":
    test_query()
