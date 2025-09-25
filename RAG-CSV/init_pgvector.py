import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Replace with your actual connection string
CONN_STR = ""



def init_pgvector_tables():
    conn = psycopg2.connect(CONN_STR)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Enable pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # Create collection table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS langchain_pg_collection (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    cmetadata JSONB
    );
    """)

    # Drop and recreate embedding table with correct schema
    cur.execute("DROP TABLE IF EXISTS langchain_pg_embedding;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID NOT NULL,
    embedding VECTOR(768), -- adjust dimension to match your model
    document TEXT,
    cmetadata JSONB,
    FOREIGN KEY (collection_id) REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables created successfully")

if __name__ == "__main__":
    init_pgvector_tables()
