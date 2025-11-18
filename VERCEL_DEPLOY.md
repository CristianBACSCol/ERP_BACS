# 🚀 Guía de Despliegue en Vercel

Esta guía te ayudará a desplegar tu aplicación Flask ERP BACS en Vercel.

## 📋 Requisitos Previos

1. **Cuenta en Vercel**: Crea una cuenta gratuita en [vercel.com](https://vercel.com)
2. **Repositorio en GitHub**: Tu código ya está en GitHub (https://github.com/CristianBACSCol/ERP_BACS)
3. **Variables de entorno**: Necesitarás configurar las variables de entorno en Vercel

## 🔧 Pasos para el Despliegue

### Paso 1: Conectar el Repositorio con Vercel

1. Ve a [vercel.com](https://vercel.com) e inicia sesión
2. Haz clic en "Add New Project"
3. Selecciona tu repositorio: `CristianBACSCol/ERP_BACS`
4. Vercel detectará automáticamente que es un proyecto Python

### Paso 2: Configurar Variables de Entorno

En la configuración del proyecto en Vercel, agrega las siguientes variables de entorno:

#### Base de Datos
```
DB_HOST=sql10.freesqldatabase.com
DB_PORT=3306
DB_USER=sql10808406
DB_PASSWORD=11jM9ivuDb
DB_NAME=sql10808406
```

#### Configuración de la Aplicación
```
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_2024
FLASK_ENV=production
FLASK_DEBUG=False
```

#### Usuario Inicial (Opcional, solo si necesitas crear el usuario admin)
```
INITIAL_USER_EMAIL=admin@tuempresa.com
INITIAL_USER_PASSWORD=tu_contraseña_segura_aqui
```

#### Cloudflare R2
```
R2_ENDPOINT_URL=https://e0ddac0321b698a6696551a5287e5392.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=5f686b73b8833569d14f23681c7c2e28
R2_SECRET_ACCESS_KEY=ebb3043c2025529682c5a48d73be62323875084371d6950475598ff736205f89
R2_BUCKET_NAME=erp-bacs
```

**⚠️ IMPORTANTE**: 
- Reemplaza `SECRET_KEY` con una clave secreta única y segura
- Asegúrate de que las credenciales de R2 sean correctas

### Paso 3: Configurar el Proyecto

En la configuración del proyecto en Vercel:

1. **Framework Preset**: Deja en blanco o selecciona "Other"
2. **Root Directory**: `.` (raíz del proyecto)
3. **Build Command**: (dejar vacío o no configurar)
4. **Output Directory**: (dejar vacío)
5. **Install Command**: `pip install -r requirements.txt`

### Paso 4: Desplegar

1. Haz clic en "Deploy"
2. Vercel comenzará a construir y desplegar tu aplicación
3. Espera a que termine el proceso (puede tomar 2-5 minutos)
4. Una vez completado, obtendrás una URL como: `https://tu-proyecto.vercel.app`

## 🔍 Verificación Post-Despliegue

### 1. Verificar que la aplicación carga

Visita la URL de tu aplicación. Deberías ver la página de login.

### 2. Verificar la conexión a la base de datos

1. Intenta hacer login con tus credenciales
2. Si es la primera vez, necesitarás ejecutar la migración de la base de datos

### 3. Ejecutar migración de base de datos (Primera vez)

**Opción A: Desde local**

Puedes ejecutar la migración desde tu máquina local antes del despliegue:

```bash
python migrar_db.py
```

**Opción B: Desde Vercel CLI**

1. Instala Vercel CLI: `npm i -g vercel`
2. Ejecuta: `vercel env pull .env.local`
3. Ejecuta localmente: `python migrar_db.py`

### 4. Verificar subida de archivos a R2

1. Intenta subir un formulario con fotos y firmas
2. Verifica en Cloudflare R2 que los archivos se suban correctamente

## ⚠️ Limitaciones y Consideraciones

### Limitaciones de Vercel (Plan Gratuito)

1. **Tiempo máximo de ejecución**: 10 segundos (Hobby plan), 30 segundos (Pro plan)
2. **Tamaño de función**: 50MB (Hobby plan), 250MB (Pro plan)
3. **Memoria**: 1024MB por defecto

### Consideraciones para tu Aplicación

1. **Archivos grandes**: Asegúrate de que la generación de PDFs y procesamiento de imágenes no exceda el tiempo límite
2. **Archivos estáticos**: Los archivos en `/static` y `/files` se servirán correctamente
3. **Sesiones**: Las sesiones de Flask funcionarán, pero pueden tener timeouts más cortos

## 🔄 Actualizaciones Futuras

Para actualizar la aplicación después del despliegue inicial:

1. Haz push a GitHub en la rama `main`
2. Vercel detectará automáticamente los cambios
3. Desplegará automáticamente una nueva versión

O manualmente:

```bash
vercel --prod
```

## 🐛 Solución de Problemas

### Error: "Module not found"

**Solución**: Verifica que todas las dependencias estén en `requirements.txt`

### Error: "Database connection failed"

**Solución**: 
1. Verifica las variables de entorno de la base de datos en Vercel
2. Asegúrate de que la base de datos MySQL permita conexiones externas

### Error: "Function timeout"

**Solución**: 
- Optimiza las operaciones que toman mucho tiempo
- Considera mover operaciones pesadas a tareas en segundo plano
- Considera actualizar a Vercel Pro para tener más tiempo (30 segundos)

### Error: "R2 upload failed"

**Solución**:
1. Verifica las credenciales de R2 en las variables de entorno
2. Asegúrate de que el bucket `erp-bacs` existe en Cloudflare R2
3. Verifica los permisos del token de R2

## 📞 Soporte

Si encuentras problemas durante el despliegue:

1. Revisa los logs de Vercel en el dashboard
2. Verifica que todas las variables de entorno estén configuradas
3. Contacta al equipo de desarrollo

---

**Desarrollado por**: Equipo de Desarrollo BACS  
**Última actualización**: Diciembre 2024

