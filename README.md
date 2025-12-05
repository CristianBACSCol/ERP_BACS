# ERP BACS - Sistema de Gestión de Incidencias

## 📋 Descripción del Sistema

El ERP BACS es un sistema de gestión empresarial desarrollado específicamente para la empresa BACS (Building Automation and Control System SAS). Este sistema permite la gestión integral de incidencias técnicas, clientes, usuarios, sedes y sistemas, proporcionando una plataforma centralizada para el seguimiento y resolución de problemas técnicos.

## 🏗️ Arquitectura del Sistema

- **Base de Datos**: Supabase (PostgreSQL) - Almacena todos los datos SQL (usuarios, clientes, formularios, incidencias, etc.)
- **Almacenamiento de Archivos**: Cloudflare R2 - Almacena imágenes, PDFs, firmas y documentos
- **Hosting**: Vercel - Plataforma de despliegue serverless

## 🚀 Instalación y Configuración

### Requisitos Previos

1. **Python 3.8 o superior** - [python.org](https://www.python.org/downloads/)
2. **Cuenta de Supabase** - [supabase.com](https://supabase.com) (para base de datos)
3. **Cuenta de Cloudflare R2** - [cloudflare.com](https://www.cloudflare.com/products/r2/) (para almacenamiento de archivos)
4. **Git** (opcional) - [git-scm.com](https://git-scm.com/downloads)

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

Crea un archivo `.env` en la raíz del proyecto. Puedes usar `env.local.example` como referencia:

```env
# Base de datos Supabase (PostgreSQL)
# ⚠️ IMPORTANTE: La conexión directa solo funciona con IPv6
# Si estás en una red IPv4 (la mayoría, incluyendo Vercel), usa Session Pooler
# Obtén estos valores de: Supabase Dashboard > Settings > Database > Connection string

# Opción 1: Session Pooler (RECOMENDADO - compatible con IPv4)
# Ve a: Supabase Dashboard > Settings > Database > Connection string
# Selecciona "Session mode" y copia la URL
DB_HOST=aws-0-us-west-2.pooler.supabase.com
DB_PORT=5432
DB_USER=postgres.tu_proyecto
DB_PASSWORD=tu_contraseña_supabase
DB_NAME=postgres

# Opción 2: Transaction Pooler (alternativa)
# Selecciona "Transaction mode" en Supabase Dashboard
# DB_HOST=aws-0-us-west-2.pooler.supabase.com
# DB_PORT=5432
# DB_USER=postgres.tu_proyecto
# DB_PASSWORD=tu_contraseña_supabase
# DB_NAME=postgres

# URL de conexión Session Pooler (RECOMENDADO - compatible IPv4)
# Obtén esta URL de: Supabase Dashboard > Connection string > Session mode
SUPABASE_DB_URL=postgresql://postgres.tu_proyecto:tu_contraseña@aws-0-us-west-2.pooler.supabase.com:5432/postgres

# Configuración de la aplicación
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_2024
FLASK_ENV=development
FLASK_DEBUG=True

# Usuario inicial del sistema
INITIAL_USER_EMAIL=admin@tuempresa.com
INITIAL_USER_PASSWORD=tu_contraseña_segura_aqui

# Cloudflare R2 (almacenamiento de archivos)
# Deja vacío para desarrollo local (usará almacenamiento local)
R2_ENDPOINT_URL=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=erp-bacs
```

**⚠️ IMPORTANTE**: El archivo `.env` está en `.gitignore` y no se subirá a GitHub.

#### 3. Configurar Base de Datos en Supabase

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Ve a **Settings** → **Database** → **Connection string**
3. **IMPORTANTE**: La conexión directa solo funciona con IPv6
4. **Para redes IPv4** (la mayoría, incluyendo Vercel): Selecciona **"Session mode"** o **"Transaction mode"**
5. Copia la URL completa que aparece
6. Configura las variables en tu `.env`

**💡 Recomendación**: Usa **Session Pooler** (puerto 6543) - es compatible con IPv4 y funciona en Vercel.

#### 4. Migración de Base de Datos

**Si tienes un backup SQL previo** (archivo `erp_bacs (1).sql`):

```bash
python migrar_supabase.py
```

Este script:
- ✅ Lee el archivo SQL de backup
- ✅ Convierte la sintaxis de MySQL a PostgreSQL
- ✅ Crea todas las tablas en Supabase
- ✅ Migra todos los datos (usuarios, clientes, formularios, respuestas, etc.)
- ✅ Configura índices y relaciones

**Si es una instalación nueva**:

```bash
python migrar_db.py
```

Este script crea las tablas y datos iniciales.

#### 5. Ejecutar Aplicación

```bash
python ejecutar_app.py
```

Accede a: `http://localhost:5000`

## 🏠 Desarrollo Local

### Configuración Local

1. **Base de datos**: Usa Supabase (remoto) - No necesitas instalar PostgreSQL localmente
2. **Almacenamiento**: Deja R2 vacío en `.env` → usa `uploads/r2_storage/` localmente
3. **Archivos**: Se guardan localmente en `uploads/r2_storage/` durante desarrollo

### Estructura Local de Archivos

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

1. Ve a **Vercel Dashboard** → Tu Proyecto → **Settings** → **Environment Variables**
2. Agrega todas las variables de tu `.env`:
   - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
   - `SUPABASE_DB_URL` (opcional, pero recomendado)
   - `SECRET_KEY`, `FLASK_ENV`, `FLASK_DEBUG`
   - `INITIAL_USER_EMAIL`, `INITIAL_USER_PASSWORD`
   - `R2_ENDPOINT_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`
3. Selecciona el entorno: **Production** (y opcionalmente Preview/Development)
4. Guarda y **redespliega** la aplicación

### Despliegue

1. Conecta tu repositorio de GitHub con Vercel
2. Vercel detectará automáticamente el proyecto
3. Configura las variables de entorno en el dashboard
4. Haz clic en **Deploy**

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
- **PostgreSQL (Supabase)** - Base de datos relacional
- **psycopg2-binary** - Driver de PostgreSQL
- **ReportLab 4.0.4** - Generación de PDFs
- **Pillow 11.3.0** - Procesamiento de imágenes
- **pillow-heif** - Soporte para formato HEIC

### Frontend
- **HTML5 + CSS3 + JavaScript** - Interfaz de usuario
- **Canvas API** - Firmas digitales
- **Responsive Design** - Adaptable a móviles

### Almacenamiento y Base de Datos
- **Supabase (PostgreSQL)** - Base de datos SQL (usuarios, clientes, formularios, etc.)
- **Cloudflare R2** - Almacenamiento de archivos (imágenes, PDFs, firmas)
- **Sistema de archivos local** - Almacenamiento en desarrollo (cuando R2 no está configurado)

## 📁 Estructura del Proyecto

```
erp_bacs/
├── app.py                     # Aplicación principal Flask
├── config.py                  # Configuración del sistema
├── r2_storage.py              # Utilidades para Cloudflare R2
├── ejecutar_app.py            # Script de ejecución
├── migrar_db.py               # Migración inicial de base de datos
├── migrar_supabase.py         # Migración de backup SQL a Supabase
├── requirements.txt           # Dependencias Python
├── vercel.json                # Configuración de Vercel
├── env.local.example          # Ejemplo de configuración local
├── env.production.example     # Ejemplo de configuración producción
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
- ✅ Las credenciales de Supabase y R2 deben mantenerse privadas

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

### Error: "Database connection failed" o "Could not connect to Supabase"
- Verifica que las credenciales de Supabase en `.env` sean correctas
- **IMPORTANTE**: La conexión directa solo funciona con IPv6
- **Para redes IPv4** (la mayoría): Usa **Session Pooler** (puerto `6543`, usuario `postgres.tu_proyecto`)
- Verifica que tu IP esté permitida en Supabase (Settings → Database → Connection Pooling)
- Prueba usar `SUPABASE_DB_URL` con la URL completa de Supabase Dashboard

### Error: "could not translate host name" o "Name or service not known"
- Este error indica que estás intentando usar conexión directa en una red IPv4
- **Solución**: Usa **Session Pooler** o **Transaction Pooler**:
  1. Ve a Supabase Dashboard > Settings > Database > Connection string
  2. Selecciona **"Session mode"** o **"Transaction mode"** (no "Direct connection")
  3. Copia la URL completa y úsala como `SUPABASE_DB_URL`
  4. O configura: `DB_PORT=6543` y `DB_USER=postgres.tu_proyecto` en tu `.env`

### Error: "Tenant or user not found"
- Este error generalmente ocurre cuando tu IP no está permitida en Supabase
- **Solución**: 
  1. Ve a Supabase Dashboard > Settings > Database > Connection Pooling
  2. Agrega tu IP a "Allowed IPs" o usa `0.0.0.0/0` temporalmente para pruebas
  3. Verifica que el usuario sea `postgres.tu_proyecto` (no solo `postgres`) para el pooler

### Error: "psycopg2 no está instalado"
```bash
pip install psycopg2-binary
```

### Error: "No se encontró el archivo erp_bacs (1).sql"
- Asegúrate de que el archivo esté en la raíz del proyecto
- Verifica que el nombre del archivo sea exactamente `erp_bacs (1).sql`

### Error: "Las credenciales de R2 no están configuradas"
- **Local**: Es normal, el sistema usará almacenamiento local en `uploads/r2_storage/`
- **Producción**: Verifica que las variables de entorno estén configuradas en Vercel

### Error: "Duplicate key" o "Unique constraint violation"
- Esto es normal si ejecutas la migración múltiples veces
- El script usa `ON CONFLICT DO NOTHING` para evitar duplicados
- Si necesitas reiniciar, puedes eliminar las tablas en Supabase y volver a ejecutar

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

# Migrar base de datos (nueva instalación)
python migrar_db.py

# Migrar desde backup SQL a Supabase
python migrar_supabase.py
```

### Mantenimiento
```bash
# Actualizar dependencias
pip install --upgrade -r requirements.txt

# Verificar dependencias
pip list
```

## 📝 Notas Importantes

1. **Base de Datos**: El sistema usa Supabase (PostgreSQL) para almacenar todos los datos SQL. No se requiere instalación local de PostgreSQL.

2. **Almacenamiento de Archivos**: Los archivos (imágenes, PDFs, firmas) se almacenan en Cloudflare R2, no en Supabase. Esto permite escalabilidad y mejor rendimiento.

3. **Desarrollo Local**: Durante el desarrollo, puedes dejar R2 sin configurar y el sistema usará almacenamiento local. La base de datos siempre se conecta a Supabase (remoto).

4. **Producción**: En producción (Vercel), tanto Supabase como Cloudflare R2 deben estar configurados correctamente.

## 📞 Soporte

Para soporte técnico o consultas sobre el sistema, contacta al equipo de desarrollo de BACS.

---

**Desarrollado por**: Equipo de Desarrollo BACS  
**Versión**: 1.0  
**Última actualización**: Diciembre 2024
