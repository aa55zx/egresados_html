import psycopg2

def apply_links():
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
            # 1. Update admin
            cur.execute("""
                UPDATE usuarios 
                SET auth_id = '759b55e6-2929-4378-a1fc-e86353440747',
                    email = 'acevedosesmaandres@gmail.com'
                WHERE username = 'admin';
            """)
            print(f"Admin update: {cur.rowcount} row(s) updated.")
            
            # 2. Update egresado
            cur.execute("""
                UPDATE usuarios 
                SET auth_id = 'e3bdce09-346d-4530-bb32-7de941e1510d',
                    email = 'acevedosesmaandresjosue@gmail.com'
                WHERE username = 'egresado';
            """)
            print(f"Egresado update: {cur.rowcount} row(s) updated.")
            
            # 3. Update empresa
            cur.execute("""
                UPDATE usuarios 
                SET auth_id = '45286ab7-b24c-4503-bd0a-e6b24f074922',
                    email = 'zengdatz@gmail.com'
                WHERE username = 'empresa';
            """)
            print(f"Empresa update: {cur.rowcount} row(s) updated.")
            
            conn.commit()
            print("Changes committed successfully.")
        conn.close()
    except Exception as e:
        print(f"Failed to apply database links: {e}")

if __name__ == "__main__":
    apply_links()
