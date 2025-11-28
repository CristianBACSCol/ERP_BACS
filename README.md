# ERP BACS - Sistema de Gestión de Incidencias

## 📋 Descripción del Sistema

El ERP BACS es un sistema de gestión empresarial desarrollado específicamente para la empresa BACS (Building Automation and Control System SAS). Este sistema permite la gestión integral de incidencias técnicas, clientes, usuarios, sedes y sistemas, proporcionando una plataforma centralizada para el seguimiento y resolución de problemas técnicos.

## 🚀 Instalación y Configuración

### Requisitos Previos

1. **Python 3.8 o superior** - [python.org](https://www.python.org/downloads/)
2. **MySQL Server** - [mysql.com](https://dev.mysql.com/downloads/mysql/) o XAMPP
3. **Git** (opcional) - [git-scm.com](https://git-scm.com/downloads)

### Instalación Automática

```bash
python setup_completo.py
```

Este script crea el entorno virtual, instala dependencias, configura la base de datos y crea el archivo `.env`.

### Instalación Manual

#### 1. Preparar Entorno

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con:

```env
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=erp_bacs

# Aplicación
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_2024
FLASK_ENV=development
FLASK_DEBUG=True

# Usuario inicial
INITIAL_USER_EMAIL=admin@tuempresa.com
INITIAL_USER_PASSWORD=tu_contraseña_segura_aqui

# Cloudflare R2 (dejar vacío para modo local)
R2_ENDPOINT_URL=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=erp-bacs
```

#### 3. Configurar Base de Datos

```sql
CREATE DATABASE erp_bacs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 4. Ejecutar Migración

```bash
python migrar_db.py
```

#### 5. Ejecutar Aplicación

```bash
python ejecutar_app.py
```

Accede a: `http://localhost:5000`

## 🏠 Desarrollo Local (XAMPP)

### Configuración Local

1. **Base de datos**: Usa MySQL de XAMPP (localhost)
2. **Almacenamiento**: Deja R2 vacío en `.env` → usa `uploads/r2_storage/`
3. **Archivos**: Se guardan localmente en `uploads/r2_storage/`

### Estructura Local

```
uploads/r2_storage/
└── Formularios/
    ├── imagenes/      (se eliminan después de generar PDF)
    ├── firmas/        (se eliminan después de generar PDF)
    └── [nombre_formulario]/
        └── documento_*.pdf  (se mantienen)
```

## 🚀 Producción (Vercel)

### Configurar Variables de Entorno en Vercel

1. Ve a Vercel Dashboard → Tu Proyecto → Settings → Environment Variables
2. Agrega las siguientes variables:

```
DB_HOST=tu_host_remoto
DB_PORT=3306
DB_USER=tu_usuario_remoto
DB_PASSWORD=tu_contraseña_remota
DB_NAME=tu_base_de_datos

SECRET_KEY=tu_clave_secreta_muy_segura_aqui_2024
FLASK_ENV=production
FLASK_DEBUG=False

INITIAL_USER_EMAIL=admin@tuempresa.com
INITIAL_USER_PASSWORD=tu_contraseña_segura_aqui

R2_ENDPOINT_URL=https://tu_endpoint.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=tu_access_key_id
R2_SECRET_ACCESS_KEY=tu_secret_access_key
R2_BUCKET_NAME=erp-bacs
```

### Despliegue

1. Conecta tu repositorio de GitHub con Vercel
2. Vercel detectará automáticamente el proyecto
3. Configura las variables de entorno
4. Haz clic en "Deploy"

## 📸 Procesamiento de Imágenes

### Formatos Soportados

- ✅ **HEIC/HEIF** (fotos de iPhone/iPad) - Requiere `pillow-heif`
- ✅ **JPEG/JPG**
- ✅ **PNG** (con transparencia)
- ✅ **GIF, BMP, TIFF, WebP** y otros formatos soportados por Pillow

### Características

- ✅ **Conversión automática a JPG**: Todos los formatos se convierten a JPG
- ✅ **Optimización de peso**: Compresión adaptativa (90% → 60% según necesidad)
- ✅ **Redimensionamiento inteligente**: Si > 4000px, redimensiona automáticamente
- ✅ **Mantiene calidad visual**: Excelente calidad, peso reducido
- ✅ **Soporte HEIC**: Instalación automática de `pillow-heif`

### Instalación de Soporte HEIC

```bash
pip install pillow-heif
```

### Optimización Automática

El sistema optimiza automáticamente las imágenes:

1. **Validación**: Verifica que el archivo < 20MB
2. **Redimensionamiento**: Si > 4000px, redimensiona manteniendo proporción
3. **Compresión adaptativa**: 
   - Comienza con calidad 90%
   - Si > 4MB, reduce calidad progresivamente (90% → 85% → 80% → ... → 60%)
   - Se detiene cuando el archivo es ≤ 4MB
4. **Redimensionamiento agresivo**: Si aún es muy grande, redimensiona a 2500px

**Resultado**: Archivos siempre < 4MB, evitando error 413 PAYLOAD_TOO_LARGE en Vercel.

## 🔧 Funcionalidades Principales

### Gestión de Usuarios
- Sistema de registro y login seguro
- Roles y permisos (Administrador, Coordinador, Técnico, Usuario)
- Gestión de perfiles

### Gestión de Clientes y Sedes
- Registro completo de empresas cliente
- Gestión de múltiples sedes por cliente
- Información detallada de contactos

### Gestión de Incidencias
- Creación de incidencias con formulario completo
- Numeración automática única
- Asignación de técnicos
- Estados de seguimiento (Abierta, En Proceso, Cerrada)
- Sistema de adjuntos con imágenes

### Formularios Dinámicos
- ✅ Creación de formularios personalizados
- ✅ Campos de firma digital (mouse y táctil)
- ✅ Campos de fotos múltiples
- ✅ Campos de texto, fechas, selección
- ✅ Generación automática de PDFs
- ✅ Datos del firmante incluidos en PDFs
- ✅ **Limpieza automática**: Imágenes y firmas se eliminan 5 segundos después de generar PDF
- ✅ **Solo PDFs permanecen**: Solo se mantienen los PDFs en la carpeta del formulario

### Generación de Informes
- Informes estructurados en PDF
- Plantillas personalizables
- Exportación de datos

## 🛠️ Tecnologías

### Backend
- **Python 3.8+** - Lenguaje principal
- **Flask 2.3.3** - Framework web
- **SQLAlchemy 3.0.5** - ORM para base de datos
- **MySQL** - Base de datos relacional
- **ReportLab 4.0.4** - Generación de PDFs
- **Pillow 11.3.0** - Procesamiento de imágenes
- **pillow-heif** - Soporte para formato HEIC

### Frontend
- **HTML5 + CSS3 + JavaScript** - Interfaz de usuario
- **Canvas API** - Firmas digitales
- **Responsive Design** - Adaptable a móviles

### Almacenamiento
- **Cloudflare R2** - Almacenamiento en producción
- **Sistema de archivos local** - Almacenamiento en desarrollo

## 📁 Estructura del Proyecto

```
erp_bacs/
├── app.py                     # Aplicación principal Flask
├── config.py                  # Configuración del sistema
├── r2_storage.py              # Utilidades para Cloudflare R2
├── ejecutar_app.py            # Script de ejecución
├── migrar_db.py               # Migración de base de datos
├── setup_completo.py          # Setup automático completo
├── requirements.txt           # Dependencias Python
├── vercel.json                # Configuración de Vercel
├── api/
│   └── index.py               # Handler para Vercel
├── static/
│   └── css/
│       └── style.css          # Estilos principales
├── templates/                 # Plantillas HTML
└── uploads/                   # Archivos subidos (local)
    └── r2_storage/            # Almacenamiento local (modo desarrollo)
```

## 🔒 Seguridad

- ⚠️ **NUNCA** subas el archivo `.env` con credenciales reales a GitHub
- ✅ El archivo `.env` está en `.gitignore` y no se subirá
- ✅ Los archivos `env.local.example` y `env.production.example` están en `.gitignore` (guárdalos localmente)
- ✅ En Vercel, configura las variables de entorno en el dashboard
- ✅ Usa contraseñas seguras y únicas

## 🐛 Solución de Problemas

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "No se puede abrir imagen HEIC"
```bash
pip install pillow-heif
```

### Error: "413 PAYLOAD_TOO_LARGE"
- El sistema optimiza automáticamente las imágenes
- Si persiste, verifica que `vercel.json` tenga los límites configurados

### Error: "Database connection failed"
- Verifica que MySQL esté corriendo (XAMPP)
- Verifica las credenciales en `.env`
- Verifica que la base de datos exista

### Error: "Las credenciales de R2 no están configuradas"
- **Local**: Es normal, el sistema usará almacenamiento local
- **Producción**: Verifica que las variables de entorno estén configuradas en Vercel

## 📊 Características de Optimización de Imágenes

### Límites Configurados
- **Tamaño máximo de subida**: 20 MB (validación antes de procesar)
- **Tamaño máximo después de optimización**: 4 MB (para Vercel)
- **Dimensión máxima inicial**: 4000px
- **Dimensión máxima agresiva**: 2500px (si aún es muy grande)

### Proceso de Optimización
1. Validación de tamaño (< 20MB)
2. Redimensionamiento si > 4000px
3. Compresión adaptativa (90% → 60% según necesidad)
4. Redimensionamiento agresivo si aún es muy grande
5. Guardado como JPG optimizado

## 🚀 Comandos Útiles

### Desarrollo
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Ejecutar aplicación
python ejecutar_app.py

# Ejecutar migración
python migrar_db.py
```

### Mantenimiento
```bash
# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Verificar dependencias
pip list
```

## 📞 Soporte

Para soporte técnico o consultas sobre el sistema, contacta al equipo de desarrollo de BACS.

---

**Desarrollado por**: Equipo de Desarrollo BACS  
**Versión**: 1.0  
**Última actualización**: Diciembre 2024
