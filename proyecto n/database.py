import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        dbname='postgres',
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()


    try:
        cursor.execute('CREATE DATABASE sistema_contable_sa')
        print(" Base de datos 'sistema_contable_sa' creada exitosamente")
    except psycopg2.Error as e:
        print(f"ℹ La base de datos ya existe o error: {e}")

    cursor.close()
    conn.close()
    
except Exception as e:
    print(f" Error conectando a PostgreSQL: {e}")
    print("Verifica que PostgreSQL esté corriendo y las credenciales en .env")