"""
Script para verificar y corregir el rol del usuario
"""
import os
import sys
from dotenv import load_dotenv  # type: ignore
from urllib.parse import quote_plus

# Cargar variables de entorno
load_dotenv()
if os.path.exists('.env.production'):
    load_dotenv('.env.production', override=True)

# Configuración de base de datos
DB_HOST = os.environ.get('DB_HOST', '').strip()
DB_PORT = os.environ.get('DB_PORT', '5432').strip()
DB_USER = os.environ.get('DB_USER', '').strip()
DB_PASSWORD = os.environ.get('DB_PASSWORD', '').strip()
DB_NAME = os.environ.get('DB_NAME', 'postgres').strip()

if not all([DB_HOST, DB_USER, DB_PASSWORD]):
    print("[ERROR] Faltan variables de entorno para la conexión")
    sys.exit(1)

escaped_password = quote_plus(DB_PASSWORD)
conn_string = f"postgresql://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    import psycopg2  # type: ignore
    
    print("=" * 80)
    print("VERIFICACION Y CORRECCION DE USUARIOS")
    print("=" * 80)
    
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    # Mostrar todos los usuarios y sus roles
    print("\n[USUARIOS Y ROLES]")
    cur.execute("""
        SELECT u.id, u.nombre, u.correo, r.id as rol_id, r.nombre as rol_nombre 
        FROM "user" u 
        JOIN rol r ON u.rol_id = r.id 
        ORDER BY u.id
    """)
    usuarios = cur.fetchall()
    for u in usuarios:
        print(f"  ID: {u[0]}, Nombre: {u[1]}, Email: {u[2]}, Rol: {u[4]} (ID: {u[3]})")
    
    # Verificar datos disponibles
    print("\n[DATOS DISPONIBLES]")
    cur.execute("SELECT COUNT(*) FROM cliente WHERE activo = true")
    clientes_count = cur.fetchone()[0]
    print(f"  Clientes activos: {clientes_count}")
    
    cur.execute("SELECT COUNT(*) FROM sede WHERE activo = true")
    sedes_count = cur.fetchone()[0]
    print(f"  Sedes activas: {sedes_count}")
    
    cur.execute("SELECT COUNT(*) FROM sistema WHERE activo = true")
    sistemas_count = cur.fetchone()[0]
    print(f"  Sistemas activos: {sistemas_count}")
    
    cur.execute("SELECT COUNT(*) FROM formulario WHERE activo = true")
    formularios_count = cur.fetchone()[0]
    print(f"  Formularios activos: {formularios_count}")
    
    cur.execute("SELECT COUNT(*) FROM incidencia")
    incidencias_count = cur.fetchone()[0]
    print(f"  Incidencias: {incidencias_count}")
    
    print("\n[NOTA]")
    print("  - Si eres Administrador (rol_id=1), deberías ver TODOS los datos")
    print("  - Si eres Coordinador (rol_id=2), deberías ver TODAS las incidencias")
    print("  - Si eres Técnico (rol_id=3), solo verás tus incidencias asignadas")
    print("  - El backup SQL original NO contenía incidencias, solo la estructura")
    print("  - Los datos básicos (clientes, sedes, sistemas) SÍ se migraron correctamente")
    
    # Opción para cambiar el rol de un usuario
    print("\n" + "=" * 80)
    print("¿Deseas cambiar el rol de algún usuario? (s/n): ", end="")
    respuesta = input().strip().lower()
    
    if respuesta == 's':
        print("\nIngresa el email del usuario a modificar: ", end="")
        email = input().strip()
        
        cur.execute("SELECT id, nombre, correo, rol_id FROM \"user\" WHERE correo = %s", (email,))
        usuario = cur.fetchone()
        
        if not usuario:
            print(f"[ERROR] No se encontró usuario con email: {email}")
        else:
            print(f"\nUsuario encontrado:")
            print(f"  ID: {usuario[0]}")
            print(f"  Nombre: {usuario[1]}")
            print(f"  Email: {usuario[2]}")
            print(f"  Rol actual ID: {usuario[3]}")
            
            print("\nRoles disponibles:")
            cur.execute("SELECT id, nombre FROM rol ORDER BY id")
            roles = cur.fetchall()
            for r in roles:
                print(f"  {r[0]}: {r[1]}")
            
            print("\nIngresa el ID del nuevo rol: ", end="")
            try:
                nuevo_rol_id = int(input().strip())
                
                # Verificar que el rol existe
                cur.execute("SELECT id FROM rol WHERE id = %s", (nuevo_rol_id,))
                if not cur.fetchone():
                    print(f"[ERROR] El rol ID {nuevo_rol_id} no existe")
                else:
                    cur.execute("UPDATE \"user\" SET rol_id = %s WHERE id = %s", (nuevo_rol_id, usuario[0]))
                    conn.commit()
                    print(f"[OK] Rol actualizado correctamente")
            except ValueError:
                print("[ERROR] Debes ingresar un número válido")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("VERIFICACION COMPLETA")
    print("=" * 80)
    
except Exception as e:
    print(f"[ERROR] Error verificando usuarios: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

