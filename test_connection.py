#!/usr/bin/env python3
"""
Script para probar la conexion a Supabase
"""

import os
import sys
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env')
load_dotenv('.env.production', override=True)

# Obtener contraseña
password = os.environ.get('DB_PASSWORD', 'BACS.2021*Col_')

# Escapar caracteres especiales
escaped_password = quote_plus(password)

print("="*80)
print("PRUEBA DE CONEXION A SUPABASE")
print("="*80)

# Intentar conexion directa primero
db_host_direct = os.environ.get('DB_HOST', 'db.maqpcjutewnqyovacqdh.supabase.co')
db_port_direct = os.environ.get('DB_PORT', '5432')
db_user_direct = os.environ.get('DB_USER', 'postgres')
db_name = os.environ.get('DB_NAME', 'postgres')

db_url_direct = f"postgresql://{db_user_direct}:{escaped_password}@{db_host_direct}:{db_port_direct}/{db_name}"

print(f"\n[OPCION 1] Conexion Directa:")
print(f"  Host: {db_host_direct}")
print(f"  Puerto: {db_port_direct}")
print(f"  Usuario: {db_user_direct}")

try:
    import psycopg2
    print("\n[INFO] Intentando conexion directa...")
    try:
        conn = psycopg2.connect(db_url_direct, connect_timeout=10)
        print("[OK] CONEXION EXITOSA con conexion directa!")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"PostgreSQL: {version[0][:50]}...")
        cur.close()
        conn.close()
        print("\n[OK] La configuracion es correcta. Puedes ejecutar migrar_supabase.py")
        sys.exit(0)
    except Exception as e1:
        print(f"[ERROR] Conexion directa fallo: {e1}")
        print("\n[INFO] Intentando con Connection Pooling...")
        
        # Intentar con pooler (Session Pooler)
        pooler_host = "aws-0-us-west-2.pooler.supabase.com"
        pooler_port = "5432"  # Session Pooler usa puerto 5432
        pooler_user = "postgres.maqpcjutewnqyovacqdh"
        pooler_url = f"postgresql://{pooler_user}:{escaped_password}@{pooler_host}:{pooler_port}/{db_name}"
        
        print(f"\n[OPCION 2] Connection Pooling:")
        print(f"  Host: {pooler_host}")
        print(f"  Puerto: {pooler_port}")
        print(f"  Usuario: {pooler_user}")
        
        try:
            conn = psycopg2.connect(pooler_url, connect_timeout=10)
            print("[OK] CONEXION EXITOSA con Connection Pooling!")
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"PostgreSQL: {version[0][:50]}...")
            cur.close()
            conn.close()
            print("\n[OK] Usa Session Pooler en tu .env:")
            print(f"DB_HOST={pooler_host}")
            print(f"DB_PORT={pooler_port}")
            print(f"DB_USER={pooler_user}")
            print(f"DB_PASSWORD={password}")
            print(f"DB_NAME={db_name}")
            sys.exit(0)
        except Exception as e2:
            print(f"[ERROR] Connection Pooling tambien fallo: {e2}")
            print("\n[INFO] Posibles soluciones:")
            print("   1. Verifica que tu IP este permitida en Supabase")
            print("      Settings > Database > Connection Pooling > Allowed IPs")
            print("   2. Verifica que la contraseña sea correcta")
            print("   3. Verifica que el proyecto este activo")
            sys.exit(1)
            
except ImportError:
    print("[ERROR] psycopg2 no esta instalado")
    print("Ejecuta: pip install psycopg2-binary")
    sys.exit(1)
