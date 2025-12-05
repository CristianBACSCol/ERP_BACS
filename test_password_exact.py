#!/usr/bin/env python3
"""
Script para verificar exactamente qué contraseña se está leyendo
"""

import os
from dotenv import load_dotenv  # type: ignore
from urllib.parse import quote_plus

load_dotenv()

password = os.environ.get('DB_PASSWORD', '')

print("="*80)
print("VERIFICACION EXACTA DE CONTRASEÑA")
print("="*80)
print(f"Contraseña leida: '{password}'")
print(f"Longitud: {len(password)} caracteres")
print(f"Representacion en bytes: {password.encode('utf-8')}")
print(f"Caracteres individuales: {[c for c in password]}")
print(f"Espacios al inicio: {len(password) - len(password.lstrip())}")
print(f"Espacios al final: {len(password) - len(password.rstrip())}")
print(f"Contraseña con .strip(): '{password.strip()}'")
print(f"Contraseña escapada: {quote_plus(password.strip())}")
print("="*80)
print("CONTRASEÑA ESPERADA: BACS.2021*Col_")
print(f"¿Coincide exactamente?: {password.strip() == 'BACS.2021*Col_'}")
print("="*80)

