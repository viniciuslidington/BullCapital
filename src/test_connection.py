import psycopg2

# Dados de conexão via proxy
host = "127.0.0.1"  # Proxy local
port = "5432"
database = "postgres"
user = "bullcapital"
password = "bullcapital"

def test_connection():
    try:
        # Conecta ao banco
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        # Cria cursor e executa algo
        cur = conn.cursor()
        cur.execute("SELECT version();")
        print("PostgreSQL version:", cur.fetchone())

        cur.close()
        conn.close()

    except Exception as e:
        print("Erro na conexão:", e)

test_connection()
