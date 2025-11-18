# 🔧 Solución de Problemas - Despliegue en Vercel

## Error: FUNCTION_INVOCATION_FAILED (500)

Si ves este error después del despliegue, sigue estos pasos:

### 1. Verificar Variables de Entorno

Asegúrate de que TODAS las variables de entorno estén configuradas en Vercel:

**En Vercel Dashboard → Settings → Environment Variables:**

#### Base de Datos (OBLIGATORIO)
```
DB_HOST=sql10.freesqldatabase.com
DB_PORT=3306
DB_USER=sql10808406
DB_PASSWORD=11jM9ivuDb
DB_NAME=sql10808406
```

#### Aplicación (OBLIGATORIO)
```
SECRET_KEY=<tu_clave_secreta_única>
FLASK_ENV=production
FLASK_DEBUG=False
```

#### Cloudflare R2 (OBLIGATORIO)
```
R2_ENDPOINT_URL=https://e0ddac0321b698a6696551a5287e5392.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=5f686b73b8833569d14f23681c7c2e28
R2_SECRET_ACCESS_KEY=ebb3043c2025529682c5a48d73be62323875084371d6950475598ff736205f89
R2_BUCKET_NAME=erp-bacs
```

### 2. Verificar Logs de Vercel

1. Ve a tu proyecto en Vercel
2. Haz clic en "Deployments"
3. Selecciona el deployment más reciente
4. Haz clic en "Functions" → `api/index.py`
5. Revisa los logs para ver el error específico

Los logs mostrarán:
- Si hay errores de importación
- Si faltan variables de entorno
- Si hay problemas con la base de datos
- Cualquier otro error de ejecución

### 3. Errores Comunes y Soluciones

#### Error: "Module not found"
**Solución**: Verifica que todas las dependencias estén en `requirements.txt`

#### Error: "Database connection failed"
**Solución**: 
- Verifica que las credenciales de la base de datos sean correctas
- Asegúrate de que la base de datos MySQL permita conexiones externas
- Verifica que el host `sql10.freesqldatabase.com` sea accesible

#### Error: "R2 credentials invalid"
**Solución**:
- Verifica que `R2_ACCESS_KEY_ID` tenga exactamente 32 caracteres
- Verifica que `R2_SECRET_ACCESS_KEY` tenga exactamente 64 caracteres
- Asegúrate de que el bucket `erp-bacs` exista en Cloudflare R2

#### Error: "SECRET_KEY not set"
**Solución**: Configura `SECRET_KEY` en las variables de entorno de Vercel

### 4. Probar la Función Localmente

Puedes probar la función localmente usando Vercel CLI:

```bash
# Instalar Vercel CLI
npm i -g vercel

# Iniciar sesión
vercel login

# Descargar variables de entorno
vercel env pull .env.local

# Probar localmente
vercel dev
```

### 5. Verificar que la Base de Datos Esté Accesible

Asegúrate de que tu base de datos MySQL permita conexiones desde las IPs de Vercel. Algunos proveedores de MySQL gratuitos tienen restricciones.

### 6. Revisar el Tamaño de la Función

Si la función excede 250MB, necesitarás:
- Optimizar dependencias (ya hecho)
- Considerar usar un servicio alternativo como Railway o Render
- Dividir la aplicación en múltiples funciones

---

**Si el problema persiste**, comparte los logs específicos de Vercel para poder ayudarte mejor.

