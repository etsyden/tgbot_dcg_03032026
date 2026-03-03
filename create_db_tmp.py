import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_db():
    # Try to connect to default 'postgres' database to create the new one
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'dental_clinic'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('CREATE DATABASE dental_clinic')
            print("Database 'dental_clinic' created successfully!")
        else:
            print("Database 'dental_clinic' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_db()
