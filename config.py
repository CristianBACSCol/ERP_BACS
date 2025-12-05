import os
from dotenv import load_dotenv  # type: ignore
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_clave_secreta_muy_segura_aqui_2024'
    
    # Configuración de base de datos - Soporta MySQL (local) y PostgreSQL (Supabase)
    DB_HOST = os.environ.get('DB_HOST', 'localhost').strip()
    DB_PORT = os.environ.get('DB_PORT', '3306').strip()
    DB_USER = os.environ.get('DB_USER', 'root').strip()
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '').strip()  # Limpiar espacios en blanco
    DB_NAME = os.environ.get('DB_NAME', 'erp_bacs').strip()
    
    # Detectar si se usa Supabase (PostgreSQL) o MySQL
    # Si hay una URL de Supabase o el puerto es 5432/6543 (PostgreSQL), usar PostgreSQL
    SUPABASE_DB_URL_ENV = os.environ.get('SUPABASE_DB_URL', '').strip() if os.environ.get('SUPABASE_DB_URL') else None
    USE_POSTGRESQL = (
        (SUPABASE_DB_URL_ENV is not None and SUPABASE_DB_URL_ENV) or 
        DB_PORT in ['5432', '6543'] or
        'supabase' in DB_HOST.lower() or
        'postgres' in DB_NAME.lower()
    )
    
    if USE_POSTGRESQL:
        # Usar PostgreSQL (Supabase)
        # Priorizar variables individuales sobre SUPABASE_DB_URL para mayor control y escape correcto
        if DB_HOST and DB_USER and DB_PASSWORD and DB_PORT and DB_NAME:
            # Construir URL desde variables individuales con contraseña escapada correctamente
            # Esto es más confiable que usar SUPABASE_DB_URL que puede tener placeholders o escape incorrecto
            
            # Escapar la contraseña correctamente (quote_plus convierte * a %2A, espacios a +, etc.)
            escaped_password = quote_plus(DB_PASSWORD)
            SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            
            # Debug: mostrar información (solo en desarrollo)
            if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == 'True':
                print(f"[DEBUG] Construyendo URL de conexión desde variables individuales:")
                print(f"  Usuario: {DB_USER}")
                print(f"  Host: {DB_HOST}")
                print(f"  Puerto: {DB_PORT}")
                print(f"  Base de datos: {DB_NAME}")
                print(f"  Contraseña (longitud): {len(DB_PASSWORD)} caracteres")
                print(f"  Contraseña escapada: {escaped_password}")
        elif SUPABASE_DB_URL_ENV and not any(placeholder in str(SUPABASE_DB_URL_ENV).upper() for placeholder in ['[YOUR', 'TU_CONTRASEÑA', '[PASSWORD]', 'YOUR_PASSWORD']):
            # Usar SUPABASE_DB_URL solo si no hay variables individuales y no tiene placeholders
            # IMPORTANTE: La contraseña en SUPABASE_DB_URL debe estar escapada manualmente
            # Ejemplo: postgresql://user:BACS.2021%2ACol_@host:port/db (donde %2A es el * escapado)
            SQLALCHEMY_DATABASE_URI = SUPABASE_DB_URL_ENV
        else:
            raise ValueError("DB_PASSWORD o variables de conexión no están configuradas. Configura DB_HOST, DB_USER, DB_PASSWORD, DB_PORT, DB_NAME en tu archivo .env")
    else:
        # Usar MySQL (desarrollo local)
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de archivos
    UPLOAD_FOLDER = 'uploads'  # Se mantiene para compatibilidad temporal, pero no se usa
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size (reducido para evitar 413 en Vercel)

    # Configuración de Cloudflare R2
    R2_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL')
    R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
    R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
    R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', 'erp-bacs')
    
    # Detectar modo local vs producción
    # Si R2 no está configurado o tiene valores por defecto, usar modo local
    R2_CONFIGURED = all([
        R2_ENDPOINT_URL,
        R2_ACCESS_KEY_ID,
        R2_SECRET_ACCESS_KEY,
        R2_ACCESS_KEY_ID != 'tu_access_key_id',
        R2_SECRET_ACCESS_KEY != 'tu_secret_access_key'
    ])
    
    # Usuario inicial
    INITIAL_USER_EMAIL = os.environ.get('INITIAL_USER_EMAIL')
    INITIAL_USER_PASSWORD = os.environ.get('INITIAL_USER_PASSWORD')
