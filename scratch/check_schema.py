import psycopg2
import psycopg2.extras

def check_schema():
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
            cur.execute("""
                SELECT column_name, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'usuarios';
            """)
            rows = cur.fetchall()
            print("Columns in 'usuarios' table:")
            for r in rows:
                print(f"  - {r['column_name']}: Nullable={r['is_nullable']}, Default={r['column_default']}")
        conn.close()
    except Exception as e:
        print(f"Schema check failed: {e}")

if __name__ == "__main__":
    check_schema()
