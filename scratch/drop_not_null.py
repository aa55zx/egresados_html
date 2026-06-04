import psycopg2

def drop_not_null():
    host = "aws-1-us-east-1.pooler.supabase.com"
    port = 6543
    user = "postgres.lgmckhssohxdqmhszgtn"
    pwd = "3G456G65H6H"
    
    try:
        conn = psycopg2.connect(
            host=host, port=port,
            dbname="postgres", user=user,
            password=pwd, sslmode="require"
        )
        with conn.cursor() as cur:
            cur.execute("ALTER TABLE usuarios ALTER COLUMN password_hash DROP NOT NULL;")
            conn.commit()
            print("Successfully dropped NOT NULL constraint from password_hash in usuarios table.")
        conn.close()
    except Exception as e:
        print(f"Failed to drop NOT NULL constraint: {e}")

if __name__ == "__main__":
    drop_not_null()
