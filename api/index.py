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
try:
    os.chdir(root_dir)
except Exception as e:
    print(f"Warning: No se pudo cambiar directorio: {e}")

# Importar la aplicación Flask con manejo de errores
try:
    from app import app
    print("✅ Aplicación Flask importada correctamente")
except Exception as e:
    print(f"❌ Error importando aplicación Flask: {e}")
    import traceback
    traceback.print_exc()
    # Crear una app Flask mínima para evitar errores
    from flask import Flask
    app = Flask(__name__)
    @app.route('/')
    def error():
        return f"Error cargando aplicación: {str(e)}", 500

# Vercel detecta automáticamente la app Flask cuando se exporta como 'app'
# No necesitamos un handler personalizado, Flask funciona directamente con Vercel

