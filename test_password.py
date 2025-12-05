#!/usr/bin/env python3
"""
Script para probar diferentes variaciones de contraseña
"""

import os
import sys
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env')
load_dotenv('.env.production', override=True)

# Obtener configuración
db_host = os.environ.get('DB_HOST', 'aws-0-us-west-2.pooler.supabase.com')
db_port = os.environ.get('DB_PORT', '5432')
db_user = os.environ.get('DB_USER', 'postgres.maqpcjutewnqyovacqdh')
db_name = os.environ.get('DB_NAME', 'postgres')

# Contraseñas a probar
passwords_to_try = [
    'BACS.2021*Col_',  # Original
    'BACS.2021*Col_',  # Sin cambios
]

print("="*80)
print("PRUEBA DE CONTRASEÑAS")
print("="*80)
print(f"\nHost: {db_host}")
print(f"Puerto: {db_port}")
print(f"Usuario: {db_user}")
print(f"\nProbando contraseñas...")

try:
    import psycopg2
    
    for password in passwords_to_try:
        escaped_password = quote_plus(password)
        db_url = f"postgresql://{db_user}:{escaped_password}@{db_host}:{db_port}/{db_name}"
        
        print(f"\n[INFO] Probando: {password}")
        print(f"       Escapada: {escaped_password}")
        
        try:
            conn = psycopg2.connect(db_url, connect_timeout=5)
            print("[OK] CONEXION EXITOSA!")
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"PostgreSQL: {version[0][:50]}...")
            cur.close()
            conn.close()
            print(f"\n[OK] La contraseña correcta es: {password}")
            print(f"\nUsa esta configuracion en tu .env:")
            print(f"DB_PASSWORD={password}")
            sys.exit(0)
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if "Wrong password" in error_msg or "password authentication failed" in error_msg:
                print(f"[ERROR] Contraseña incorrecta")
            else:
                print(f"[ERROR] {error_msg}")
        except Exception as e:
            print(f"[ERROR] {e}")
    
    print("\n" + "="*80)
    print("[ERROR] Ninguna contraseña funciono")
    print("="*80)
    print("\n[INFO] Posibles soluciones:")
    print("   1. Verifica la contraseña en Supabase Dashboard")
    print("      Settings > Database > Reset database password")
    print("   2. La contraseña puede tener caracteres especiales diferentes")
    print("   3. Puede que necesites resetear la contraseña en Supabase")
    print("\n[INFO] Para resetear la contraseña:")
    print("   1. Ve a: https://supabase.com/dashboard/project/maqpcjutewnqyovacqdh/settings/database")
    print("   2. Busca 'Reset database password'")
    print("   3. Resetea la contraseña y actualiza tu .env")
    
except ImportError:
    print("[ERROR] psycopg2 no esta instalado")
    print("Ejecuta: pip install psycopg2-binary")
    sys.exit(1)

