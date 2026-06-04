import psycopg2
import psycopg2.extras

def check_auth_users():
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
        with conn.cursor() as cur:
            # Query auth.users table in Supabase
            cur.execute("""
                SELECT id, email, encrypted_password, confirmed_at, created_at
                FROM auth.users;
            """)
            rows = cur.fetchall()
            print("Users in Supabase Auth (auth.users):")
            print(f"Total auth users found: {len(rows)}")
            for r in rows:
                print(f"  - Email: {r['email']}")
                print(f"    ID (UUID): {r['id']}")
                print(f"    Confirmed At: {r['confirmed_at']}")
                print(f"    Created At: {r['created_at']}")
        conn.close()
    except Exception as e:
        print(f"Auth schema check failed: {e}")

if __name__ == "__main__":
    check_auth_users()
