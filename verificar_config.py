#!/usr/bin/env python3
"""
Script para verificar la configuración de la base de datos
"""

import os
from dotenv import load_dotenv  # type: ignore
from urllib.parse import quote_plus

# Cargar .env
load_dotenv()

print("="*80)
print("VERIFICACIÓN DE CONFIGURACIÓN DE BASE DE DATOS")
print("="*80)

# Leer variables
DB_HOST = os.environ.get('DB_HOST', '').strip()
DB_PORT = os.environ.get('DB_PORT', '').strip()
DB_USER = os.environ.get('DB_USER', '').strip()
DB_PASSWORD = os.environ.get('DB_PASSWORD', '').strip()
DB_NAME = os.environ.get('DB_NAME', '').strip()
SUPABASE_DB_URL = os.environ.get('SUPABASE_DB_URL', '').strip() if os.environ.get('SUPABASE_DB_URL') else None

print("\n[VARIABLES DEL .env]")
print(f"  DB_HOST: {DB_HOST or 'NO CONFIGURADO'}")
print(f"  DB_PORT: {DB_PORT or 'NO CONFIGURADO'}")
print(f"  DB_USER: {DB_USER or 'NO CONFIGURADO'}")
print(f"  DB_PASSWORD: {'***' if DB_PASSWORD else 'NO CONFIGURADO'} (longitud: {len(DB_PASSWORD)})")
print(f"  DB_NAME: {DB_NAME or 'NO CONFIGURADO'}")
print(f"  SUPABASE_DB_URL: {'Configurado' if SUPABASE_DB_URL else 'NO CONFIGURADO'}")

# Verificar contraseña
if DB_PASSWORD:
    print(f"\n[ANÁLISIS DE CONTRASEÑA]")
    print(f"  Contraseña original: {DB_PASSWORD}")
    print(f"  Contraseña escapada: {quote_plus(DB_PASSWORD)}")
    print(f"  Caracteres especiales detectados: {[c for c in DB_PASSWORD if c in '*@#%&+=']}")
    
    # Construir URL
    escaped_password = quote_plus(DB_PASSWORD)
    url_construida = f"postgresql://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    url_safe = f"postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"\n[URL CONSTRUIDA]")
    print(f"  {url_safe}")
    
    # Verificar si SUPABASE_DB_URL tiene la contraseña correcta
    if SUPABASE_DB_URL:
        print(f"\n[SUPABASE_DB_URL]")
        if any(p in SUPABASE_DB_URL.upper() for p in ['[YOUR', 'TU_CONTRASEÑA', '[PASSWORD]']):
            print("  [WARNING] SUPABASE_DB_URL tiene placeholders - se usara DB_PASSWORD")
        else:
            print("  [OK] SUPABASE_DB_URL configurado - se usara esta URL")
            url_safe_env = SUPABASE_DB_URL.split('@')[0] + '@***' if '@' in SUPABASE_DB_URL else SUPABASE_DB_URL
            print(f"  {url_safe_env}")

print("\n" + "="*80)
print("RECOMENDACIONES:")
print("="*80)
if not DB_PASSWORD:
    print("  [ERROR] DB_PASSWORD no esta configurado")
    print("     Configura DB_PASSWORD=BACS.2021*Col_ en tu archivo .env")
elif DB_PASSWORD != 'BACS.2021*Col_':
    print(f"  [WARNING] La contraseña parece diferente a la esperada")
    print(f"     Verifica que sea: BACS.2021*Col_")
    
if not SUPABASE_DB_URL or any(p in SUPABASE_DB_URL.upper() for p in ['[YOUR', 'TU_CONTRASEÑA', '[PASSWORD]']):
    print("\n  [INFO] Usa variables individuales (DB_HOST, DB_USER, DB_PASSWORD, etc.)")
    print("     El script escapara automaticamente la contraseña")
else:
    print("\n  [INFO] Si usas SUPABASE_DB_URL, asegurate de que la contraseña este escapada:")
    print("     * se convierte en %2A")
    print("     Ejemplo: postgresql://user:BACS.2021%2ACol_@host:port/db")

print("="*80)

