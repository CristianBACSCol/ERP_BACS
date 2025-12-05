"""
Script para verificar qué datos se migraron a Supabase
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
    print("VERIFICACION DE DATOS EN SUPABASE")
    print("=" * 80)
    
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    # Verificar usuarios
    print("\n[USUARIOS]")
    cur.execute("SELECT id, nombre, correo, rol_id FROM \"user\" ORDER BY id")
    usuarios = cur.fetchall()
    print(f"Total usuarios: {len(usuarios)}")
    for u in usuarios:
        print(f"  ID: {u[0]}, Nombre: {u[1]}, Email: {u[2]}, Rol ID: {u[3]}")
    
    # Verificar roles
    print("\n[ROLES]")
    cur.execute("SELECT id, nombre FROM rol ORDER BY id")
    roles = cur.fetchall()
    print(f"Total roles: {len(roles)}")
    for r in roles:
        print(f"  ID: {r[0]}, Nombre: {r[1]}")
    
    # Verificar clientes
    print("\n[CLIENTES]")
    cur.execute("SELECT id, nombre, activo FROM cliente ORDER BY id")
    clientes = cur.fetchall()
    print(f"Total clientes: {len(clientes)}")
    activos = [c for c in clientes if c[2]]
    print(f"Clientes activos: {len(activos)}")
    for c in clientes[:10]:  # Mostrar primeros 10
        estado = "ACTIVO" if c[2] else "INACTIVO"
        print(f"  ID: {c[0]}, Nombre: {c[1]}, Estado: {estado}")
    if len(clientes) > 10:
        print(f"  ... y {len(clientes) - 10} más")
    
    # Verificar sedes
    print("\n[SEDES]")
    cur.execute("SELECT id, nombre, cliente_id, activo FROM sede ORDER BY id")
    sedes = cur.fetchall()
    print(f"Total sedes: {len(sedes)}")
    activas = [s for s in sedes if s[3]]
    print(f"Sedes activas: {len(activas)}")
    for s in sedes[:10]:  # Mostrar primeros 10
        estado = "ACTIVA" if s[3] else "INACTIVA"
        print(f"  ID: {s[0]}, Nombre: {s[1]}, Cliente ID: {s[2]}, Estado: {estado}")
    if len(sedes) > 10:
        print(f"  ... y {len(sedes) - 10} más")
    
    # Verificar sistemas
    print("\n[SISTEMAS]")
    cur.execute("SELECT id, nombre, activo FROM sistema ORDER BY id")
    sistemas = cur.fetchall()
    print(f"Total sistemas: {len(sistemas)}")
    activos = [s for s in sistemas if s[2]]
    print(f"Sistemas activos: {len(activos)}")
    for s in sistemas[:10]:  # Mostrar primeros 10
        estado = "ACTIVO" if s[2] else "INACTIVO"
        print(f"  ID: {s[0]}, Nombre: {s[1]}, Estado: {estado}")
    if len(sistemas) > 10:
        print(f"  ... y {len(sistemas) - 10} más")
    
    # Verificar incidencias
    print("\n[INCIDENCIAS]")
    cur.execute("SELECT id, titulo, cliente_id, estado, tecnico_asignado, creado_por FROM incidencia ORDER BY id")
    incidencias = cur.fetchall()
    print(f"Total incidencias: {len(incidencias)}")
    for i in incidencias[:10]:  # Mostrar primeros 10
        print(f"  ID: {i[0]}, Título: {i[1][:30] if i[1] else 'N/A'}, Cliente: {i[2]}, Estado: {i[3]}, Técnico: {i[4]}, Creado por: {i[5]}")
    if len(incidencias) > 10:
        print(f"  ... y {len(incidencias) - 10} más")
    
    # Verificar formularios
    print("\n[FORMULARIOS]")
    cur.execute("SELECT id, nombre, activo FROM formulario ORDER BY id")
    formularios = cur.fetchall()
    print(f"Total formularios: {len(formularios)}")
    activos = [f for f in formularios if f[2]]
    print(f"Formularios activos: {len(activos)}")
    for f in formularios[:10]:  # Mostrar primeros 10
        estado = "ACTIVO" if f[2] else "INACTIVO"
        print(f"  ID: {f[0]}, Nombre: {f[1]}, Estado: {estado}")
    if len(formularios) > 10:
        print(f"  ... y {len(formularios) - 10} más")
    
    # Verificar usuario actual y su rol
    print("\n[VERIFICACION DE USUARIO ACTUAL]")
    print("Por favor, ingresa el email del usuario con el que estás entrando:")
    email_usuario = input("Email: ").strip()
    
    if email_usuario:
        cur.execute("SELECT u.id, u.nombre, u.correo, r.nombre as rol_nombre FROM \"user\" u JOIN rol r ON u.rol_id = r.id WHERE u.correo = %s", (email_usuario,))
        usuario = cur.fetchone()
        if usuario:
            print(f"\nUsuario encontrado:")
            print(f"  ID: {usuario[0]}")
            print(f"  Nombre: {usuario[1]}")
            print(f"  Email: {usuario[2]}")
            print(f"  Rol: {usuario[3]}")
            
            # Ver qué puede ver este usuario
            if usuario[3] in ['Administrador', 'Coordinador']:
                print(f"\n[PERMISOS] Este usuario debería ver TODOS los datos (es {usuario[3]})")
            else:
                print(f"\n[PERMISOS] Este usuario solo verá sus incidencias asignadas (es {usuario[3]})")
                cur.execute("SELECT COUNT(*) FROM incidencia WHERE tecnico_asignado = %s", (usuario[0],))
                count = cur.fetchone()[0]
                print(f"  Incidencias asignadas a este usuario: {count}")
        else:
            print(f"[ERROR] No se encontró usuario con email: {email_usuario}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("VERIFICACION COMPLETA")
    print("=" * 80)
    
except Exception as e:
    print(f"[ERROR] Error verificando datos: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

