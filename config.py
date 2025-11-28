import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_clave_secreta_muy_segura_aqui_2024'
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'erp_bacs')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de archivos
    UPLOAD_FOLDER = 'uploads'  # Se mantiene para compatibilidad temporal, pero no se usa
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
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
