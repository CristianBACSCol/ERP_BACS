"""
Script para arreglar las secuencias de PostgreSQL después de la migración
"""
import os
import sys
from dotenv import load_dotenv  # type: ignore
from urllib.parse import quote_plus

# Cargar variables de entorno
load_dotenv()
if os.path.exists('.env.production'):
    load_dotenv('.env.production', override=True)

# Configuración de base de datos
DB_HOST = os.environ.get('DB_HOST', '').strip()
DB_PORT = os.environ.get('DB_PORT', '5432').strip()
DB_USER = os.environ.get('DB_USER', '').strip()
DB_PASSWORD = os.environ.get('DB_PASSWORD', '').strip()
DB_NAME = os.environ.get('DB_NAME', 'postgres').strip()

if not all([DB_HOST, DB_USER, DB_PASSWORD]):
    print("[ERROR] Faltan variables de entorno para la conexion")
    sys.exit(1)

escaped_password = quote_plus(DB_PASSWORD)
conn_string = f"postgresql://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    import psycopg2  # type: ignore
    
    print("=" * 80)
    print("ARREGLANDO SECUENCIAS DE POSTGRESQL")
    print("=" * 80)
    
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    # Tablas que necesitan secuencias arregladas
    tablas = [
        'respuesta_formulario',
        'respuesta_campo',
        'formulario',
        'campo_formulario',
        'incidencia',
        'cliente',
        'sede',
        'sistema',
        'user',
        'rol'
    ]
    
    for tabla in tablas:
        try:
            # Obtener el máximo ID actual
            cur.execute(f'SELECT COALESCE(MAX(id), 0) FROM "{tabla}"')
            max_id = cur.fetchone()[0]
            
            # Obtener el nombre de la secuencia
            cur.execute(f"""
                SELECT pg_get_serial_sequence('"{tabla}"', 'id')
            """)
            seq_result = cur.fetchone()
            
            if seq_result and seq_result[0]:
                seq_name = seq_result[0].split('.')[1]  # Obtener solo el nombre de la secuencia
                
                # Establecer el valor de la secuencia al máximo ID + 1
                nuevo_valor = max_id + 1
                cur.execute(f"SELECT setval('{seq_name}', {nuevo_valor}, false)")
                
                print(f"[OK] {tabla}: Max ID = {max_id}, Secuencia ajustada a {nuevo_valor}")
            else:
                print(f"[WARNING] {tabla}: No se encontro secuencia para esta tabla")
        except Exception as e:
            print(f"[ERROR] {tabla}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("SECUENCIAS ARREGLADAS EXITOSAMENTE")
    print("=" * 80)
    
except Exception as e:
    print(f"[ERROR] Error arreglando secuencias: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

