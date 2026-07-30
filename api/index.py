"""
Entry point para Vercel serverless functions
Este archivo permite ejecutar la aplicación Flask en Vercel
"""
import sys
import os
from flask import Flask
import traceback

# Asegurar que el directorio raíz esté en el path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Cambiar el directorio de trabajo al raíz del proyecto
try:
    os.chdir(root_dir)
except Exception as e:
    print(f"Warning: No se pudo cambiar directorio: {e}")

# Definir app a nivel superior para que Vercel lo detecte
app = None
import_error = None
try:
    from app import app as flask_app
    app = flask_app
    print("✅ Aplicación Flask importada correctamente")
except Exception as e:
    import_error = str(e)
    print(f"❌ Error importando aplicación Flask: {e}")
    traceback.print_exc()
    # Crear una app Flask mínima para evitar errores
    app = Flask(__name__)

    @app.route('/')
    def error():
        error_msg = import_error if import_error else "Error desconocido al cargar la aplicación"
        return f"Error cargando aplicación: {error_msg}", 500

# Vercel detecta automáticamente la app Flask cuando se exporta como 'app'
# No necesitamos un handler personalizado, Flask funciona directamente con Vercel

