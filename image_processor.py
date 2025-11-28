"""
Módulo para procesar, convertir y optimizar imágenes
Soporta múltiples formatos incluyendo HEIC/HEIF
"""
from PIL import Image as PILImage
from io import BytesIO
import os

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
MAX_FILE_SIZE = 0.5 * 1024 * 1024  # 0.5MB máximo
MAX_DIMENSION_INITIAL = 2000  # px
MAX_DIMENSION_AGGRESSIVE = 1200  # px
QUALITY_START = 85
QUALITY_MIN = 20


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
    Procesar, convertir y optimizar una imagen
    
    Args:
        file_data: bytes de la imagen
        filename: nombre del archivo (opcional, para detectar formato)
        max_size: tamaño máximo en bytes (default: 0.5MB)
    
    Returns:
        tuple: (bytes_optimizados, info_dict)
        info_dict contiene: original_size, optimized_size, format, dimensions, quality_used
    """
    if not file_data:
        raise ValueError("file_data no puede estar vacío")
    
    # Detectar formato por extensión
    file_extension = os.path.splitext(filename)[1].lower() if filename else ''
    is_heic = file_extension in ['.heic', '.heif']
    
    # Si es HEIC y no hay soporte, lanzar error
    if is_heic and not HEIC_SUPPORTED:
        raise ValueError(
            "Imagen HEIC detectada pero pillow-heif no está instalado. "
            "Instala con: pip install pillow-heif"
        )
    
    original_size = len(file_data)
    info = {
        'original_size': original_size,
        'original_format': file_extension or 'unknown',
        'is_heic': is_heic
    }
    
    # Abrir imagen
    try:
        img = PILImage.open(BytesIO(file_data))
        info['original_dimensions'] = img.size
        info['original_mode'] = img.mode
        info['detected_format'] = img.format
    except PILImage.UnidentifiedImageError:
        raise ValueError(f"No se pudo identificar el formato de la imagen. Asegúrate de que sea una imagen válida.")
    except Exception as e:
        if is_heic:
            raise ValueError(
                f"Error al abrir imagen HEIC: {str(e)}. "
                "Verifica que pillow-heif esté instalado correctamente."
            )
        raise ValueError(f"Error al abrir imagen: {str(e)}")
    
    # Convertir a RGB si es necesario
    if img.mode in ('RGBA', 'LA', 'P'):
        # Crear fondo blanco para imágenes con transparencia
        bg = PILImage.new("RGB", img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode == 'RGBA':
            bg.paste(img, mask=img.split()[3])
        else:
            bg.paste(img)
        img = bg
    elif img.mode not in ('RGB', 'L'):
        if img.mode == 'L':  # Escala de grises
            img = img.convert('RGB')
        else:
            img = img.convert('RGB')
    
    # Redimensionar si es necesario
    width, height = img.size
    needs_resize = False
    
    if width > MAX_DIMENSION_INITIAL or height > MAX_DIMENSION_INITIAL:
        needs_resize = True
        if width > height:
            new_width = MAX_DIMENSION_INITIAL
            new_height = int(height * (MAX_DIMENSION_INITIAL / width))
        else:
            new_height = MAX_DIMENSION_INITIAL
            new_width = int(width * (MAX_DIMENSION_INITIAL / height))
        img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
        info['resized'] = True
        info['new_dimensions'] = img.size
    
    # Optimizar con compresión adaptativa
    img_buffer = BytesIO()
    quality = QUALITY_START
    optimized_size = 0
    quality_levels = [85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20]
    
    for q in quality_levels:
        img_buffer.seek(0)
        img_buffer.truncate(0)
        
        img.save(
            img_buffer,
            format='JPEG',
            quality=q,
            optimize=True,
            progressive=True
        )
        
        optimized_size = len(img_buffer.getvalue())
        
        if optimized_size <= max_size:
            quality = q
            info['quality_used'] = quality
            info['optimized_size'] = optimized_size
            break
    
    # Si aún es muy grande, redimensionar más agresivamente
    if optimized_size > max_size:
        print(f"DEBUG: Archivo aún muy grande ({optimized_size / 1024:.1f} KB), redimensionando más agresivamente...")
        
        if width > MAX_DIMENSION_AGGRESSIVE or height > MAX_DIMENSION_AGGRESSIVE:
            if width > height:
                new_width = MAX_DIMENSION_AGGRESSIVE
                new_height = int(height * (MAX_DIMENSION_AGGRESSIVE / width))
            else:
                new_height = MAX_DIMENSION_AGGRESSIVE
                new_width = int(width * (MAX_DIMENSION_AGGRESSIVE / height))
            img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            info['aggressive_resize'] = True
            info['final_dimensions'] = img.size
        
        # Intentar de nuevo con calidades más bajas
        for q in [40, 35, 30, 25, 20]:
            img_buffer.seek(0)
            img_buffer.truncate(0)
            img.save(
                img_buffer,
                format='JPEG',
                quality=q,
                optimize=True,
                progressive=True
            )
            optimized_size = len(img_buffer.getvalue())
            if optimized_size <= max_size:
                quality = q
                info['quality_used'] = quality
                info['optimized_size'] = optimized_size
                break
        else:
            # Usar la mejor calidad encontrada aunque sea > max_size
            quality = 20
            info['quality_used'] = quality
            info['optimized_size'] = optimized_size
            info['warning'] = f"Archivo optimizado aún es grande: {optimized_size / 1024:.1f} KB"
    
    img_buffer.seek(0)
    optimized_data = img_buffer.getvalue()
    
    # Calcular reducción
    reduction = ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0
    info['reduction_percent'] = round(reduction, 1)
    info['format'] = 'JPEG'
    
    print(f"DEBUG: Imagen procesada - Original: {original_size / 1024:.1f} KB, "
          f"Optimizado: {optimized_size / 1024:.1f} KB ({optimized_size / 1024 / 1024:.2f} MB), "
          f"Reducción: {reduction:.1f}%, Calidad: {quality}%")
    
    return optimized_data, info

