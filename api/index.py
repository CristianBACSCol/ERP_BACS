"""
Entry point para Vercel serverless functions
Este archivo permite ejecutar la aplicación Flask en Vercel
"""
import sys
import os

# Asegurar que el directorio raíz esté en el path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Cambiar el directorio de trabajo al raíz del proyecto
os.chdir(root_dir)

# Importar la aplicación Flask
from app import app

# Vercel espera que la app Flask se exporte directamente
# Vercel manejará automáticamente las rutas

