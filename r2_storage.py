"""
Módulo de utilidades para Cloudflare R2 (compatible con S3)
"""
import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from io import BytesIO
import tempfile
from flask import current_app


def get_r2_client():
    """Crea y retorna un cliente de boto3 configurado para Cloudflare R2"""
    endpoint_url = os.environ.get('R2_ENDPOINT_URL')
    access_key_id = os.environ.get('R2_ACCESS_KEY_ID')
    secret_access_key = os.environ.get('R2_SECRET_ACCESS_KEY')
    
    if not all([endpoint_url, access_key_id, secret_access_key]):
        raise ValueError("Las credenciales de R2 no están configuradas correctamente. Verifica R2_ENDPOINT_URL, R2_ACCESS_KEY_ID y R2_SECRET_ACCESS_KEY en el archivo .env")
    
    # Validar formato de credenciales
    if access_key_id == 'tu_access_key_id' or len(access_key_id) != 32:
        raise ValueError(f"R2_ACCESS_KEY_ID inválido. Debe tener 32 caracteres. Longitud actual: {len(access_key_id)}. Verifica el archivo .env")
    
    if secret_access_key == 'tu_secret_access_key' or len(secret_access_key) != 64:
        raise ValueError(f"R2_SECRET_ACCESS_KEY inválido. Debe tener 64 caracteres. Longitud actual: {len(secret_access_key)}. Verifica el archivo .env")
    
    s3_config = Config(
        signature_version='s3v4',
        s3={
            'addressing_style': 'path'
        }
    )
    
    return boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        config=s3_config
    )


def get_bucket_name():
    """Retorna el nombre del bucket de R2"""
    return os.environ.get('R2_BUCKET_NAME', 'erp-bacs')


def upload_file_to_r2(file_data, r2_path, content_type=None):
    """
    Sube un archivo a R2
    
    Args:
        file_data: BytesIO, archivo de Flask, bytes, o ruta de archivo local
        r2_path: Ruta del archivo en R2 (ej: 'Formularios/formulario.pdf')
        content_type: Tipo MIME del archivo (opcional)
    
    Returns:
        bool: True si la subida fue exitosa, False en caso contrario
    """
    try:
        s3_client = get_r2_client()
        bucket_name = get_bucket_name()
        
        # Convertir diferentes tipos de entrada a bytes
        if isinstance(file_data, str):
            # Es una ruta de archivo local
            with open(file_data, 'rb') as f:
                body = f.read()
        elif hasattr(file_data, 'read'):
            # Es un objeto de archivo (BytesIO, Flask file, etc.)
            if hasattr(file_data, 'seek'):
                file_data.seek(0)
            body = file_data.read()
        elif isinstance(file_data, bytes):
            body = file_data
        else:
            raise ValueError(f"Tipo de datos no soportado: {type(file_data)}")
        
        # Determinar content_type si no se proporciona
        if not content_type:
            import mimetypes
            content_type, _ = mimetypes.guess_type(r2_path)
            if not content_type:
                content_type = 'application/octet-stream'
        
        # Subir a R2
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=r2_path,
                Body=body,
                ContentType=content_type
            )
            return True
        except Exception as upload_error:
            # Si el error es de credenciales, proporcionar mensaje más claro
            error_str = str(upload_error)
            if 'Credential' in error_str or 'access key' in error_str.lower():
                print(f"ERROR subiendo archivo a R2 {r2_path}: Error de credenciales. Verifica R2_ACCESS_KEY_ID y R2_SECRET_ACCESS_KEY en el archivo .env")
                print(f"  Detalle: {error_str}")
            else:
                print(f"ERROR subiendo archivo a R2 {r2_path}: {error_str}")
            return False
    except ValueError as ve:
        # Error de validación de credenciales
        print(f"ERROR subiendo archivo a R2 {r2_path}: {str(ve)}")
        return False
    except Exception as e:
        print(f"ERROR subiendo archivo a R2 {r2_path}: {str(e)}")
        return False


def download_file_from_r2(r2_path):
    """
    Descarga un archivo de R2 y retorna los bytes
    
    Args:
        r2_path: Ruta del archivo en R2
    
    Returns:
        bytes: Contenido del archivo, o None si no existe
    """
    try:
        s3_client = get_r2_client()
        bucket_name = get_bucket_name()
        
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=r2_path
        )
        
        return response['Body'].read()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"Archivo no encontrado en R2: {r2_path}")
        else:
            print(f"ERROR descargando archivo de R2 {r2_path}: {str(e)}")
        return None
    except Exception as e:
        print(f"ERROR descargando archivo de R2 {r2_path}: {str(e)}")
        return None


def get_file_url_from_r2(r2_path, expires_in=3600):
    """
    Genera una URL presignada para acceder a un archivo en R2
    
    Args:
        r2_path: Ruta del archivo en R2
        expires_in: Tiempo de expiración en segundos (default: 1 hora)
    
    Returns:
        str: URL presignada, o None si hay error
    """
    try:
        s3_client = get_r2_client()
        bucket_name = get_bucket_name()
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': r2_path
            },
            ExpiresIn=expires_in
        )
        
        return url
    except Exception as e:
        print(f"ERROR generando URL presignada para {r2_path}: {str(e)}")
        return None


def file_exists_in_r2(r2_path):
    """
    Verifica si un archivo existe en R2
    
    Args:
        r2_path: Ruta del archivo en R2
    
    Returns:
        bool: True si existe, False en caso contrario
    """
    try:
        s3_client = get_r2_client()
        bucket_name = get_bucket_name()
        
        s3_client.head_object(
            Bucket=bucket_name,
            Key=r2_path
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        print(f"ERROR verificando archivo en R2 {r2_path}: {str(e)}")
        return False
    except Exception as e:
        print(f"ERROR verificando archivo en R2 {r2_path}: {str(e)}")
        return False


def delete_file_from_r2(r2_path):
    """
    Elimina un archivo de R2
    
    Args:
        r2_path: Ruta del archivo en R2
    
    Returns:
        bool: True si se eliminó exitosamente, False en caso contrario
    """
    try:
        s3_client = get_r2_client()
        bucket_name = get_bucket_name()
        
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=r2_path
        )
        return True
    except Exception as e:
        print(f"ERROR eliminando archivo de R2 {r2_path}: {str(e)}")
        return False


def download_to_temp_file(r2_path):
    """
    Descarga un archivo de R2 a un archivo temporal
    
    Args:
        r2_path: Ruta del archivo en R2
    
    Returns:
        str: Ruta del archivo temporal, o None si hay error
    """
    try:
        file_data = download_file_from_r2(r2_path)
        if file_data is None:
            return None
        
        # Crear archivo temporal
        suffix = os.path.splitext(r2_path)[1] or '.tmp'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(file_data)
        temp_file.close()
        
        return temp_file.name
    except Exception as e:
        print(f"ERROR descargando archivo temporal de R2 {r2_path}: {str(e)}")
        return None

