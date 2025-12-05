#!/usr/bin/env python3
"""
Script para migrar la base de datos MySQL a Supabase (PostgreSQL)
Este script:
1. Lee el archivo SQL de MySQL
2. Convierte la sintaxis a PostgreSQL
3. Crea las tablas en Supabase
4. Migra todos los datos
"""

import os
import sys
import re
from urllib.parse import quote_plus

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def convertir_mysql_a_postgresql(sql_content):
    """
    Convierte sintaxis MySQL a PostgreSQL
    """
    # Remover comentarios de MySQL
    sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
    sql_content = re.sub(r'--.*', '', sql_content)
    
    # Remover ENGINE y CHARSET
    sql_content = re.sub(r'ENGINE=\w+\s*', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'DEFAULT CHARSET=\w+\s*', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'COLLATE=\w+', '', sql_content, flags=re.IGNORECASE)
    
    # Convertir tipos de datos
    sql_content = re.sub(r'\bint\(11\)\b', 'INTEGER', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'\bvarchar\((\d+)\)\b', r'VARCHAR(\1)', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'\btext\b', 'TEXT', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'\bdatetime\b', 'TIMESTAMP', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'\btinyint\(1\)\b', 'BOOLEAN', sql_content, flags=re.IGNORECASE)
    
    # Convertir AUTO_INCREMENT a SERIAL
    # Primero, identificar tablas con AUTO_INCREMENT
    auto_increment_pattern = r'MODIFY\s+`(\w+)`\s+int\(11\)\s+NOT\s+NULL\s+AUTO_INCREMENT.*?AUTO_INCREMENT=(\d+);'
    matches = re.finditer(auto_increment_pattern, sql_content, re.IGNORECASE | re.DOTALL)
    
    # Convertir DEFAULT NULL a NULL
    sql_content = re.sub(r'DEFAULT\s+NULL', 'NULL', sql_content, flags=re.IGNORECASE)
    
    # Convertir backticks a comillas dobles (PostgreSQL)
    sql_content = sql_content.replace('`', '"')
    
    # Remover SET SQL_MODE, START TRANSACTION, COMMIT, etc.
    sql_content = re.sub(r'SET\s+SQL_MODE[^;]*;', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'START\s+TRANSACTION;', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'COMMIT;', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'SET\s+time_zone[^;]*;', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'SET\s+CHARACTER_SET[^;]*;', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'SET\s+COLLATION[^;]*;', '', sql_content, flags=re.IGNORECASE)
    
    # Remover AUTO_INCREMENT de ALTER TABLE
    sql_content = re.sub(r'ALTER\s+TABLE[^;]*AUTO_INCREMENT[^;]*;', '', sql_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Convertir ADD KEY a CREATE INDEX (se hará después)
    # Por ahora, solo remover ADD KEY de ALTER TABLE
    sql_content = re.sub(r'ADD\s+KEY\s+[^,)]+', '', sql_content, flags=re.IGNORECASE)
    sql_content = re.sub(r'ADD\s+UNIQUE\s+KEY\s+[^,)]+', '', sql_content, flags=re.IGNORECASE)
    
    # Limpiar ALTER TABLE que quedaron vacíos
    sql_content = re.sub(r'ALTER\s+TABLE\s+"\w+"\s*;', '', sql_content, flags=re.IGNORECASE)
    
    return sql_content

def extraer_inserts(sql_content):
    """Extrae todos los INSERT statements"""
    inserts = []
    pattern = r'INSERT\s+INTO\s+"?(\w+)"?\s*\([^)]+\)\s*VALUES\s*([^;]+);'
    matches = re.finditer(pattern, sql_content, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        table = match.group(1)
        values = match.group(2)
        inserts.append((table, values))
    
    return inserts

def crear_tablas_postgresql():
    """
    Crea las tablas en PostgreSQL con la estructura correcta
    """
    return """
-- Tabla: rol
CREATE TABLE IF NOT EXISTS "rol" (
    "id" SERIAL PRIMARY KEY,
    "nombre" VARCHAR(50) NOT NULL UNIQUE,
    "descripcion" TEXT
);

-- Tabla: user
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL PRIMARY KEY,
    "nombre" VARCHAR(100) NOT NULL,
    "tipo_documento" VARCHAR(20) NOT NULL,
    "numero_documento" VARCHAR(20) NOT NULL UNIQUE,
    "telefono" VARCHAR(20) NOT NULL,
    "correo" VARCHAR(120) NOT NULL UNIQUE,
    "password_hash" VARCHAR(128),
    "rol_id" INTEGER NOT NULL REFERENCES "rol"("id"),
    "fecha_creacion" TIMESTAMP
);

-- Tabla: cliente
CREATE TABLE IF NOT EXISTS "cliente" (
    "id" SERIAL PRIMARY KEY,
    "nombre" VARCHAR(200) NOT NULL,
    "tipo_documento" VARCHAR(20) NOT NULL,
    "numero_documento" VARCHAR(20) NOT NULL UNIQUE,
    "correo" VARCHAR(120) NOT NULL,
    "telefono" VARCHAR(20) NOT NULL,
    "direccion" TEXT,
    "contacto_principal" VARCHAR(100),
    "cargo_contacto" VARCHAR(100),
    "fecha_creacion" TIMESTAMP,
    "activo" BOOLEAN
);

-- Tabla: sede
CREATE TABLE IF NOT EXISTS "sede" (
    "id" SERIAL PRIMARY KEY,
    "cliente_id" INTEGER NOT NULL REFERENCES "cliente"("id"),
    "nombre" VARCHAR(200) NOT NULL,
    "direccion" TEXT,
    "telefono" VARCHAR(20),
    "correo" VARCHAR(120),
    "contacto_responsable" VARCHAR(100),
    "cargo_responsable" VARCHAR(100),
    "fecha_creacion" TIMESTAMP,
    "activo" BOOLEAN
);

-- Tabla: sistema
CREATE TABLE IF NOT EXISTS "sistema" (
    "id" SERIAL PRIMARY KEY,
    "nombre" VARCHAR(100) NOT NULL UNIQUE,
    "descripcion" TEXT,
    "activo" BOOLEAN,
    "fecha_creacion" TIMESTAMP
);

-- Tabla: indice
CREATE TABLE IF NOT EXISTS "indice" (
    "id" SERIAL PRIMARY KEY,
    "prefijo" VARCHAR(10) NOT NULL,
    "numero_actual" INTEGER,
    "formato" VARCHAR(20)
);

-- Tabla: formulario
CREATE TABLE IF NOT EXISTS "formulario" (
    "id" SERIAL PRIMARY KEY,
    "nombre" VARCHAR(200) NOT NULL,
    "descripcion" TEXT,
    "activo" BOOLEAN,
    "fecha_creacion" TIMESTAMP,
    "creado_por" INTEGER NOT NULL REFERENCES "user"("id")
);

-- Tabla: campo_formulario
CREATE TABLE IF NOT EXISTS "campo_formulario" (
    "id" SERIAL PRIMARY KEY,
    "formulario_id" INTEGER NOT NULL REFERENCES "formulario"("id"),
    "tipo_campo" VARCHAR(50) NOT NULL,
    "titulo" VARCHAR(200) NOT NULL,
    "descripcion" TEXT,
    "obligatorio" BOOLEAN,
    "orden" INTEGER,
    "configuracion" TEXT
);

-- Tabla: respuesta_formulario
CREATE TABLE IF NOT EXISTS "respuesta_formulario" (
    "id" SERIAL PRIMARY KEY,
    "formulario_id" INTEGER NOT NULL REFERENCES "formulario"("id"),
    "diligenciado_por" INTEGER NOT NULL REFERENCES "user"("id"),
    "fecha_diligenciamiento" TIMESTAMP,
    "estado" VARCHAR(20),
    "archivo_pdf" VARCHAR(500)
);

-- Tabla: respuesta_campo
CREATE TABLE IF NOT EXISTS "respuesta_campo" (
    "id" SERIAL PRIMARY KEY,
    "respuesta_formulario_id" INTEGER NOT NULL REFERENCES "respuesta_formulario"("id"),
    "campo_id" INTEGER NOT NULL REFERENCES "campo_formulario"("id"),
    "valor_texto" TEXT,
    "valor_fecha" TIMESTAMP,
    "valor_archivo" VARCHAR(500),
    "valor_json" TEXT,
    "nombre_firmante" VARCHAR(100),
    "documento_firmante" VARCHAR(20),
    "telefono_firmante" VARCHAR(20),
    "empresa_firmante" VARCHAR(100),
    "cargo_firmante" VARCHAR(100)
);

-- Tabla: incidencia
CREATE TABLE IF NOT EXISTS "incidencia" (
    "id" SERIAL PRIMARY KEY,
    "indice" VARCHAR(20) NOT NULL UNIQUE,
    "titulo" VARCHAR(200) NOT NULL,
    "descripcion" TEXT NOT NULL,
    "fecha_inicio" TIMESTAMP,
    "fecha_cambio_estado" TIMESTAMP,
    "estado" VARCHAR(20),
    "tecnico_asignado" INTEGER REFERENCES "user"("id"),
    "creado_por" INTEGER NOT NULL REFERENCES "user"("id"),
    "cliente_id" INTEGER NOT NULL REFERENCES "cliente"("id"),
    "sede_id" INTEGER NOT NULL REFERENCES "sede"("id"),
    "sistema_id" INTEGER NOT NULL REFERENCES "sistema"("id"),
    "adjuntos" TEXT,
    "titulos_imagenes" TEXT,
    "configuracion_imagenes" TEXT
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_formulario_creado_por ON "formulario"("creado_por");
CREATE INDEX IF NOT EXISTS idx_campo_formulario_formulario_id ON "campo_formulario"("formulario_id");
CREATE INDEX IF NOT EXISTS idx_respuesta_formulario_formulario_id ON "respuesta_formulario"("formulario_id");
CREATE INDEX IF NOT EXISTS idx_respuesta_formulario_diligenciado_por ON "respuesta_formulario"("diligenciado_por");
CREATE INDEX IF NOT EXISTS idx_respuesta_campo_respuesta_formulario_id ON "respuesta_campo"("respuesta_formulario_id");
CREATE INDEX IF NOT EXISTS idx_respuesta_campo_campo_id ON "respuesta_campo"("campo_id");
CREATE INDEX IF NOT EXISTS idx_incidencia_tecnico_asignado ON "incidencia"("tecnico_asignado");
CREATE INDEX IF NOT EXISTS idx_incidencia_creado_por ON "incidencia"("creado_por");
CREATE INDEX IF NOT EXISTS idx_incidencia_cliente_id ON "incidencia"("cliente_id");
CREATE INDEX IF NOT EXISTS idx_incidencia_sede_id ON "incidencia"("sede_id");
CREATE INDEX IF NOT EXISTS idx_incidencia_sistema_id ON "incidencia"("sistema_id");
CREATE INDEX IF NOT EXISTS idx_sede_cliente_id ON "sede"("cliente_id");
CREATE INDEX IF NOT EXISTS idx_user_rol_id ON "user"("rol_id");
"""

def migrar_datos_desde_sql():
    """
    Función principal para migrar la base de datos a Supabase
    """
    print("=" * 80)
    print("MIGRACIÓN DE BASE DE DATOS MYSQL A SUPABASE (POSTGRESQL)")
    print("=" * 80)
    
    # Verificar que existe el archivo SQL
    sql_file = 'erp_bacs (1).sql'
    if not os.path.exists(sql_file):
        print(f"ERROR: No se encontró el archivo {sql_file}")
        return 1
    
    # Verificar configuración de Supabase
    from dotenv import load_dotenv  # type: ignore
    # Cargar .env primero (desarrollo local), luego .env.production si existe (sobrescribe)
    # IMPORTANTE: Solo cargar .env.production si realmente existe y tiene valores reales
    load_dotenv('.env')
    # Solo cargar .env.production si existe y no tiene placeholders
    if os.path.exists('.env.production'):
        # Verificar que no tenga placeholders antes de cargar
        with open('.env.production', 'r', encoding='utf-8') as f:
            prod_content = f.read()
            # Si tiene valores reales (no placeholders), cargarlo
            if 'tu_contraseña' not in prod_content.lower() and '[YOUR-PASSWORD]' not in prod_content.upper() and '[PASSWORD]' not in prod_content.upper():
                load_dotenv('.env.production', override=True)
    
    db_url = os.environ.get('SUPABASE_DB_URL')
    # Si SUPABASE_DB_URL tiene placeholders, ignorarlo y usar variables individuales
    if db_url and ('tu_contraseña' in db_url.lower() or 'your_password' in db_url.lower() or '[password]' in db_url.lower() or '[YOUR-PASSWORD]' in db_url.upper() or '[YOUR_PASSWORD]' in db_url.upper()):
        print("[INFO] SUPABASE_DB_URL tiene un placeholder, usando variables individuales...")
        db_url = None
    
    # Debug: mostrar qué variables se están usando
    print(f"[DEBUG] DB_HOST: {os.environ.get('DB_HOST', 'NO CONFIGURADO')}")
    print(f"[DEBUG] DB_USER: {os.environ.get('DB_USER', 'NO CONFIGURADO')}")
    print(f"[DEBUG] DB_PASSWORD: {'***' if os.environ.get('DB_PASSWORD') else 'NO CONFIGURADO'}")
    print(f"[DEBUG] SUPABASE_DB_URL: {'Configurado' if db_url and '[YOUR' not in db_url.upper() else 'NO CONFIGURADO o con placeholder'}")
    
    if not db_url:
        # Construir URL desde variables individuales
        db_host = os.environ.get('DB_HOST', 'aws-0-us-west-2.pooler.supabase.com')
        db_port = os.environ.get('DB_PORT', '5432')  # Session Pooler usa puerto 5432
        db_user = os.environ.get('DB_USER', 'postgres.maqpcjutewnqyovacqdh')
        db_password = os.environ.get('DB_PASSWORD', 'BACS.2021*Col_')
        db_name = os.environ.get('DB_NAME', 'postgres')
        
        if not all([db_host, db_user, db_password]):
            print("\nERROR: Credenciales de Supabase no configuradas")
            print("Por favor configura en .env:")
            print("   SUPABASE_DB_URL=postgresql://user:password@host:port/db")
            print("   O las variables individuales: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME")
            print("\n[INFO] NOTA IMPORTANTE:")
            print("   Si tu red es IPv4 (la mayoría), usa Session Pooler o Transaction Pooler")
            print("   La conexión directa solo funciona con IPv6")
            print("   En Supabase Dashboard > Settings > Database > Connection string")
            print("   Selecciona 'Session mode' o 'Transaction mode' y copia la URL")
            return 1
        
        # Escapar contraseña correctamente
        escaped_password = quote_plus(db_password)
        db_url = f"postgresql://{db_user}:{escaped_password}@{db_host}:{db_port}/{db_name}"
        
        # Debug adicional
        print(f"[DEBUG] URL construida (sin contraseña): postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
        print(f"[DEBUG] Contraseña original: {db_password}")
        print(f"[DEBUG] Contraseña escapada: {escaped_password}")
    
    # Mostrar información de conexión (sin contraseña)
    connection_info = db_url.split('@')[1] if '@' in db_url else 'URL oculta'
    print(f"Conectando a Supabase: {connection_info}")
    
    # Debug: mostrar información de conexión (sin contraseña)
    print(f"\n[DEBUG] Variables leidas del .env:")
    print(f"  DB_HOST: {os.environ.get('DB_HOST', 'NO ENCONTRADO')}")
    print(f"  DB_PORT: {os.environ.get('DB_PORT', 'NO ENCONTRADO')}")
    print(f"  DB_USER: {os.environ.get('DB_USER', 'NO ENCONTRADO')}")
    print(f"  DB_PASSWORD: {'*** (configurado)' if os.environ.get('DB_PASSWORD') else 'NO ENCONTRADO'}")
    print(f"  DB_NAME: {os.environ.get('DB_NAME', 'NO ENCONTRADO')}")
    if db_url and '@' in db_url:
        url_parts = db_url.split('@')
        if len(url_parts) == 2:
            user_pass = url_parts[0].split('://')[1] if '://' in url_parts[0] else url_parts[0]
            user_only = user_pass.split(':')[0] if ':' in user_pass else user_pass
            print(f"\n[DEBUG] URL construida:")
            print(f"  Usuario: {user_only}")
            print(f"  Host: {connection_info.split(':')[0]}")
            print(f"  Puerto: {connection_info.split(':')[1].split('/')[0] if ':' in connection_info else 'N/A'}")
    
    try:
        import psycopg2  # type: ignore
    except ImportError:
        print("ERROR: psycopg2 no está instalado")
        print("Ejecuta: pip install psycopg2-binary")
        return 1
    
    try:
        # Leer archivo SQL
        print(f"\nLeyendo archivo SQL: {sql_file}...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Conectar a Supabase
        print("Conectando a Supabase...")
        try:
            # Intentar conectar con timeout
            conn = psycopg2.connect(db_url, connect_timeout=10)
            conn.autocommit = False
            cur = conn.cursor()
            print("[OK] Conexion exitosa a Supabase")
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            print(f"[ERROR] Error de conexion: {error_msg}")
            
            # Si es error de "Tenant or user not found", sugerir usar conexión directa
            if "Tenant or user not found" in error_msg or "not found" in error_msg.lower():
                print("\n[INFO] SOLUCION: Este error generalmente ocurre con el pooler.")
                print("   Para migraciones, usa la conexion DIRECTA:")
                print("   1. Ve a Supabase Dashboard > Settings > Database")
                print("   2. Selecciona 'Connection string' > 'Direct connection'")
                print("   3. Copia la URL completa y usala como SUPABASE_DB_URL")
                print("   4. O cambia DB_PORT a 5432 y DB_USER a 'postgres'")
            
            # Si es error de resolución de host (IPv4 vs IPv6)
            if "could not translate host name" in error_msg or "Name or service not known" in error_msg:
                print("\n" + "="*80)
                print("[INFO] SOLUCION: Problema de IPv4/IPv6")
                print("="*80)
                print("\nLa conexion directa solo funciona con IPv6.")
                print("Si estas en una red IPv4 (la mayoria), usa Session Pooler o Transaction Pooler.")
                print("\n[PASOS]:")
                print("   1. Ve a: https://supabase.com/dashboard/project/maqpcjutewnqyovacqdh")
                print("   2. Ve a: Settings > Database > Connection string")
                print("   3. En 'Method', selecciona 'Session mode' o 'Transaction mode'")
                print("   4. Copia la URL completa que aparece")
                print("\nLa URL deberia verse asi:")
                print("   postgresql://postgres.maqpcjutewnqyovacqdh:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres")
                print("\nLuego en tu archivo .env, usa:")
                print("   SUPABASE_DB_URL=postgresql://postgres.maqpcjutewnqyovacqdh:[PASSWORD]@[HOST_POOLER]:5432/postgres")
                print("\n   O usa variables individuales:")
                print("   DB_HOST=aws-0-[REGION].pooler.supabase.com")
                print("   DB_PORT=5432")
                print("   DB_USER=postgres.maqpcjutewnqyovacqdh")
                print("   DB_PASSWORD=[PASSWORD]")
                print("   DB_NAME=postgres")
                print("="*80)
            
            # Si es error de contraseña incorrecta
            if "Wrong password" in error_msg or "password authentication failed" in error_msg:
                print("\n[ERROR] Contraseña incorrecta")
                print("[INFO] Verifica:")
                print("   1. Que la contraseña en tu .env sea correcta")
                print("   2. Que no haya espacios extra al inicio o final")
                print("   3. Que los caracteres especiales esten correctos")
                print("\n[DEBUG] Informacion de conexion:")
                if db_password:
                    print(f"   Contraseña leida: {db_password[:3]}...{db_password[-3:] if len(db_password) > 6 else '***'} (longitud: {len(db_password)})")
                if db_host:
                    print(f"   Host: {db_host}")
                if db_user:
                    print(f"   Usuario: {db_user}")
                print("\n[INFO] Prueba ejecutar: python test_connection.py")
                print("   Ese script funciona, copia la misma configuracion a tu .env")
                print("\n[INFO] Asegurate de que tu archivo .env tenga:")
                print("   DB_HOST=aws-0-us-west-2.pooler.supabase.com")
                print("   DB_PORT=5432")
                print("   DB_USER=postgres.maqpcjutewnqyovacqdh")
                print("   DB_PASSWORD=BACS.2021*Col_")
                print("   DB_NAME=postgres")
            
            raise
        
        # Crear tablas
        print("\nCreando tablas en Supabase...")
        create_tables_sql = crear_tablas_postgresql()
        cur.execute(create_tables_sql)
        conn.commit()  # Hacer commit de la creación de tablas
        print("[OK] Tablas creadas correctamente")
        
        # Leer y procesar datos del SQL
        print("\nProcesando datos del archivo SQL...")
        
        # Extraer INSERT statements
        insert_pattern = r'INSERT\s+INTO\s+`?(\w+)`?\s*\(([^)]+)\)\s*VALUES\s*([^;]+);'
        matches = list(re.finditer(insert_pattern, sql_content, re.IGNORECASE | re.DOTALL))
        
        print(f"Encontrados {len(matches)} bloques de INSERT")
        
        # Orden de inserción basado en dependencias de claves foráneas
        # Las tablas sin dependencias primero, luego las que dependen de ellas
        orden_insercion = [
            'rol',           # Sin dependencias
            'sistema',       # Sin dependencias
            'indice',        # Sin dependencias
            'user',          # Depende de rol
            'formulario',    # Depende de user
            'campo_formulario',  # Depende de formulario
            'respuesta_formulario',  # Depende de formulario y user
            'respuesta_campo',  # Depende de respuesta_formulario y campo_formulario
        ]
        
        # Agrupar INSERTs por tabla
        inserts_por_tabla = {}
        
        for match in matches:
            table_name = match.group(1).lower()
            columns = match.group(2)
            values_block = match.group(3)
            
            # Limpiar columnas (remover backticks)
            columns = re.sub(r'`', '', columns)
            column_list = [col.strip() for col in columns.split(',')]
            
            # Procesar valores
            # Dividir por filas (separadas por ),( o ),\n
            rows = re.split(r'\),\s*\(', values_block)
            rows[0] = rows[0].lstrip('(')
            rows[-1] = rows[-1].rstrip(')')
            
            # Inicializar estructura para esta tabla si no existe
            if table_name not in inserts_por_tabla:
                inserts_por_tabla[table_name] = {
                    'columns': column_list,
                    'rows': []
                }
            
            # Agregar filas a la tabla
            for row in rows:
                row = row.strip()
                if not row:
                    continue
                
                # Parsear valores
                values = []
                in_string = False
                current_value = ""
                i = 0
                
                while i < len(row):
                    char = row[i]
                    
                    if char == "'" and (i == 0 or row[i-1] != '\\'):
                        in_string = not in_string
                        current_value += char
                    elif char == ',' and not in_string:
                        values.append(current_value.strip())
                        current_value = ""
                    else:
                        current_value += char
                    i += 1
                
                if current_value:
                    values.append(current_value.strip())
                
                # Convertir valores
                processed_values = []
                for idx, val in enumerate(values):
                    val = val.strip()
                    if val.upper() == 'NULL':
                        processed_values.append(None)
                    elif val.startswith("'") and val.endswith("'"):
                        # String - remover comillas y escapar
                        val = val[1:-1].replace("''", "'").replace("\\'", "'")
                        processed_values.append(val)
                    elif val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                        # Número entero
                        processed_values.append(int(val))
                    elif '.' in val and val.replace('.', '').replace('-', '').isdigit():
                        # Número decimal
                        processed_values.append(float(val))
                    else:
                        # Otros valores (mantener como string)
                        processed_values.append(val)
                
                # Convertir valores booleanos si la columna es de tipo boolean
                # MySQL usa TINYINT(1) con valores 0/1, PostgreSQL usa BOOLEAN
                boolean_columns = ['activo', 'obligatorio', 'completado', 'habilitado', 'visible', 'publicado']  # Columnas que son booleanas
                for idx, col in enumerate(column_list):
                    if col.lower() in boolean_columns and idx < len(processed_values):
                        val = processed_values[idx]
                        # Convertir 0/1, '0'/'1', o False/True a boolean
                        if val is None:
                            processed_values[idx] = None
                        elif val == 0 or val == '0' or (isinstance(val, str) and val.strip() == '0'):
                            processed_values[idx] = False
                        elif val == 1 or val == '1' or (isinstance(val, str) and val.strip() == '1'):
                            processed_values[idx] = True
                        elif isinstance(val, str) and val.upper().strip() == 'NULL':
                            processed_values[idx] = None
                        # Si ya es boolean, mantenerlo
                        elif isinstance(val, bool):
                            pass
                        else:
                            # Intentar convertir string a boolean
                            try:
                                processed_values[idx] = bool(int(val))
                            except (ValueError, TypeError):
                                # Si no se puede convertir, mantener el valor original
                                pass
                
                # Agregar fila procesada a la tabla
                inserts_por_tabla[table_name]['rows'].append(processed_values)
        
        # Procesar e insertar datos en el orden correcto
        tablas_procesadas = {}
        
        # Primero procesar tablas en el orden definido
        for table_name in orden_insercion:
            if table_name not in inserts_por_tabla:
                continue
            
            print(f"\n[INFO] Procesando tabla: {table_name}")
            table_data = inserts_por_tabla[table_name]
            column_list = table_data['columns']
            rows = table_data['rows']
            
            if table_name not in tablas_procesadas:
                tablas_procesadas[table_name] = 0
            
            for processed_values in rows:
                # Validar que el número de valores coincida con el número de columnas
                if len(processed_values) != len(column_list):
                    print(f"  [WARNING] Error insertando en {table_name}: Número de valores ({len(processed_values)}) no coincide con número de columnas ({len(column_list)})")
                    print(f"     Columnas esperadas: {len(column_list)}")
                    print(f"     Valores recibidos: {len(processed_values)}")
                    print(f"     Valores: {processed_values[:3]}...")
                    continue
                
                # Insertar en PostgreSQL
                try:
                    placeholders = ','.join(['%s'] * len(column_list))
                    columns_str = ','.join([f'"{col}"' for col in column_list])
                    insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
                    cur.execute(insert_sql, processed_values)
                    tablas_procesadas[table_name] += 1
                except Exception as e:
                    print(f"  [WARNING] Error insertando en {table_name}: {e}")
                    print(f"     Valores: {processed_values[:3]}...")
                    conn.rollback()
                    continue
            
            # Commit después de cada tabla para evitar problemas
            conn.commit()
            print(f"  [OK] {table_name}: {tablas_procesadas[table_name]} registros insertados")
        
        # Procesar tablas que no están en el orden definido (por si hay otras tablas)
        for table_name, table_data in inserts_por_tabla.items():
            if table_name in orden_insercion:
                continue  # Ya procesada
            
            print(f"\n[INFO] Procesando tabla adicional: {table_name}")
            column_list = table_data['columns']
            rows = table_data['rows']
            
            if table_name not in tablas_procesadas:
                tablas_procesadas[table_name] = 0
            
            for processed_values in rows:
                # Validar que el número de valores coincida con el número de columnas
                if len(processed_values) != len(column_list):
                    print(f"  [WARNING] Error insertando en {table_name}: Número de valores ({len(processed_values)}) no coincide con número de columnas ({len(column_list)})")
                    print(f"     Columnas esperadas: {len(column_list)}")
                    print(f"     Valores recibidos: {len(processed_values)}")
                    print(f"     Valores: {processed_values[:3]}...")
                    continue
                
                try:
                    placeholders = ','.join(['%s'] * len(column_list))
                    columns_str = ','.join([f'"{col}"' for col in column_list])
                    insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
                    cur.execute(insert_sql, processed_values)
                    tablas_procesadas[table_name] += 1
                except Exception as e:
                    print(f"  [WARNING] Error insertando en {table_name}: {e}")
                    print(f"     Valores: {processed_values[:3]}...")
                    conn.rollback()
                    continue
            
            conn.commit()
            print(f"  [OK] {table_name}: {tablas_procesadas[table_name]} registros insertados")
        
        print("\n[OK] Datos migrados correctamente")
        
        # Resumen
        print("\n" + "=" * 80)
        print("RESUMEN DE MIGRACIÓN:")
        print("=" * 80)
        for tabla, count in sorted(tablas_procesadas.items()):
            print(f"  {tabla}: {count} registros")
        print("=" * 80)
        print("\n[OK] MIGRACION COMPLETADA EXITOSAMENTE!")
        print("\nAhora puedes configurar las variables de entorno en Vercel y desplegar.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\nERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(migrar_datos_desde_sql())

