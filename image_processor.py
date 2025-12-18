"""
Módulo para procesar, convertir y optimizar imágenes
Soporta múltiples formatos incluyendo HEIC/HEIF
Prioriza la calidad de imagen y solo comprime si excede el límite de 1MB.
"""
from PIL import Image as PILImage
from io import BytesIO
import os
import math

# Intentar registrar soporte para HEIC/HEIF
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False
    print("ADVERTENCIA: pillow-heif no está instalado. Las imágenes HEIC no podrán ser procesadas.")
except Exception as e:
    HEIC_SUPPORTED = False
    print(f"ADVERTENCIA: Error registrando soporte HEIC: {e}")

# Formatos permitidos
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.heif', '.bmp', '.tiff', '.tif'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
    'image/heic', 'image/heif', 'image/bmp', 'image/tiff'
}

# Configuración de optimización
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB máximo (Límite estricto)
# No limitar dimensiones artificialmente a menos que sea necesario para cumplir el peso
MAX_DIMENSION_LIMIT = 4096 # Límite de seguridad para evitar DoS con imágenes gigantes (4k)


def is_image_allowed(filename, mime_type=None):
    """Verificar si el archivo es una imagen permitida"""
    if not filename:
        return False
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    
    if mime_type and mime_type.lower() not in ALLOWED_MIME_TYPES:
        return False
    
    return True


def process_image(file_data, filename=None, max_size=MAX_FILE_SIZE):
    """
    Procesar, convertir y optimizar una imagen.
    Estrategia:
    1. Si pesa <= max_size y es formato web (JPG, PNG, WEBP), devolver original (CALIDAD TOTAL).
    2. Si pesa > max_size o es HEIC/BMP/TIFF:
       - Convertir a JPEG.
       - Intentar bajar calidad progresivamente (95 -> 70) manteniendo dimensiones.
       - Si aún > max_size, reducir dimensiones progresivamente (10% por paso) hasta encajar.
    
    Returns:
        tuple: (bytes_optimizados, info_dict)
    """
    if not file_data:
        raise ValueError("file_data no puede estar vacío")
    
    original_size = len(file_data)
    file_extension = os.path.splitext(filename)[1].lower() if filename else ''
    
    # 1. CHEQUEO RÁPIDO: Si ya cumple el peso y es formato web compatible, NO TOCAR.
    if original_size <= max_size:
        if file_extension in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            info = {
                'original_size': original_size,
                'original_format': file_extension,
                'optimized_size': original_size,
                'quality_used': 'Original (Sin cambios)',
                'format': file_extension[1:].upper() if file_extension else 'UNKNOWN',
                'skipped': True,
                'reduction_percent': 0
            }
            print(f"DEBUG: Imagen {filename} pesa {original_size/1024:.1f}KB (<1MB). Se conserva original.")
            return file_data, info
    
    # --- Comienza Procesamiento --- (Solo si > 1MB o formato incompatible)
    
    is_heic = file_extension in ['.heic', '.heif']
    
    # Si es HEIC y no hay soporte, lanzar error
    if is_heic and not HEIC_SUPPORTED:
        raise ValueError("Imagen HEIC detectada pero pillow-heif no está instalado.")
        
    info = {
        'original_size': original_size,
        'original_format': file_extension or 'unknown',
        'is_heic': is_heic
    }
    
    # Abrir imagen
    try:
        img = PILImage.open(BytesIO(file_data))
        info['original_dimensions'] = img.size
        
        # Corregir orientación EXIF si existe
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except:
            pass
            
    except Exception as e:
        raise ValueError(f"Error al abrir imagen: {str(e)}")
    
    # ESTRATEGIA: Convertir todo a JPEG si se necesita comprimir
    # (PNG/WebP grandes se pasan a JPEG para lograr 1MB sin perder demasiada resolución)
    if img.mode in ('RGBA', 'LA', 'P'):
        bg = PILImage.new("RGB", img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode == 'RGBA':
            bg.paste(img, mask=img.split()[3])
        else:
            bg.paste(img)
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')
        
    # Límite de seguridad inicial (reducir 8K a 4K si es necesario, pero mantener alta res)
    width, height = img.size
    if width > MAX_DIMENSION_LIMIT or height > MAX_DIMENSION_LIMIT:
        img.thumbnail((MAX_DIMENSION_LIMIT, MAX_DIMENSION_LIMIT), PILImage.Resampling.LANCZOS)
        print(f"DEBUG: Imagen gigante reducida a {MAX_DIMENSION_LIMIT}px por seguridad.")
    
    # --- ALGORITMO DE COMPRESIÓN INTELIGENTE ---
    
    img_buffer = BytesIO()
    optimized_data = None
    final_quality = 0
    final_dims = img.size
    
    # Paso 1: Intentar ajustar SOLO bajando calidad (manteniendo resolución original)
    # Probamos calidades altas: 95, 90, 85, 80, 75
    # No bajamos de 75 en este paso para no pixelar la imagen full-res.
    print(f"DEBUG: Intentando optimizar {filename} (Original: {original_size/1024/1024:.2f}MB) manteniendo resolución...")
    
    qualities_to_try = [95, 90, 85, 80]
    success_step_1 = False
    
    for q in qualities_to_try:
        img_buffer.decode = None 
        img_buffer.seek(0)
        img_buffer.truncate(0)
        
        img.save(img_buffer, format='JPEG', quality=q, optimize=True)
        size = img_buffer.tell()
        
        if size <= max_size:
            optimized_data = img_buffer.getvalue()
            final_quality = q
            success_step_1 = True
            print(f"DEBUG: Éxito con calidad {q}. Tamaño: {size/1024:.1f}KB")
            break
            
    # Paso 2: Si aún es grande, reducir dimensiones y calidad progresivamente
    if not success_step_1:
        print("DEBUG: Paso 1 insuficiente. Iniciando redimensionamiento progresivo...")
        # Empezamos con la imagen actual y calidad decente (85) y vamos bajando escala
        # Escalas: 90%, 80%, 70%... hasta 30%
        
        current_img = img
        original_w, original_h = img.size
        
        for scale in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]:
            new_w = int(original_w * scale)
            new_h = int(original_h * scale)
            
            resized_img = img.resize((new_w, new_h), PILImage.Resampling.LANCZOS)
            
            # Probar con calidad 85 (buena) y 75 (aceptable)
            for q in [85, 75]:
                img_buffer.seek(0)
                img_buffer.truncate(0)
                resized_img.save(img_buffer, format='JPEG', quality=q, optimize=True)
                size = img_buffer.tell()
                
                if size <= max_size:
                    optimized_data = img_buffer.getvalue()
                    final_quality = q
                    final_dims = (new_w, new_h)
                    print(f"DEBUG: Éxito escalando al {int(scale*100)}% ({new_w}x{new_h}) con calidad {q}. Tamaño: {size/1024:.1f}KB")
                    break
            
            if optimized_data:
                break
                
        # MALLA DE SEGURIDAD: Si NADA funcionó (imagen extremadamente compleja o pequeña pero pesada)
        if not optimized_data:
            print("WARNING: Compresión difícil. Forzando redimensionamiento agresivo.")
            # Redimensionar a 1024px y calidad 60 (garantiza <1MB casi siempre)
            img.thumbnail((1024, 1024), PILImage.Resampling.LANCZOS)
            img_buffer.seek(0)
            img_buffer.truncate(0)
            img.save(img_buffer, format='JPEG', quality=65, optimize=True)
            optimized_data = img_buffer.getvalue()
            final_quality = 65
            final_dims = img.size

    # Resultado final
    final_size = len(optimized_data)
    reduction = ((original_size - final_size) / original_size * 100)
    
    info['optimized_size'] = final_size
    info['quality_used'] = final_quality
    info['final_dimensions'] = final_dims
    info['reduction_percent'] = round(reduction, 1)
    info['format'] = 'JPEG'
    
    return optimized_data, info

