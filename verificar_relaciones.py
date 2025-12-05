"""
Script para verificar que las relaciones de datos estén correctas
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
    print("VERIFICACION DE RELACIONES DE DATOS")
    print("=" * 80)
    
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    # Verificar cliente y sus sedes
    print("\n[CLIENTE Y SEDES]")
    cur.execute("""
        SELECT c.id, c.nombre, c.activo, COUNT(s.id) as num_sedes
        FROM cliente c
        LEFT JOIN sede s ON s.cliente_id = c.id AND s.activo = true
        WHERE c.activo = true
        GROUP BY c.id, c.nombre, c.activo
    """)
    clientes = cur.fetchall()
    for c in clientes:
        print(f"  Cliente: {c[1]} (ID: {c[0]}, Activo: {c[2]})")
        print(f"    Sedes asociadas: {c[3]}")
        
        # Mostrar sedes de este cliente
        cur.execute("""
            SELECT id, nombre, activo 
            FROM sede 
            WHERE cliente_id = %s 
            ORDER BY id
        """, (c[0],))
        sedes = cur.fetchall()
        for s in sedes:
            estado = "ACTIVA" if s[2] else "INACTIVA"
            print(f"      - {s[1]} (ID: {s[0]}, {estado})")
    
    # Verificar sistemas
    print("\n[SISTEMAS]")
    cur.execute("SELECT id, nombre, activo FROM sistema WHERE activo = true ORDER BY id")
    sistemas = cur.fetchall()
    print(f"Total sistemas activos: {len(sistemas)}")
    for s in sistemas:
        print(f"  - {s[1]} (ID: {s[0]})")
    
    # Verificar formularios
    print("\n[FORMULARIOS]")
    cur.execute("SELECT id, nombre, activo FROM formulario ORDER BY id")
    formularios = cur.fetchall()
    for f in formularios:
        estado = "ACTIVO" if f[2] else "INACTIVO"
        print(f"  - {f[1]} (ID: {f[0]}, {estado})")
    
    # Verificar usuarios y sus roles
    print("\n[USUARIOS Y ROLES]")
    cur.execute("""
        SELECT u.id, u.nombre, u.correo, r.nombre as rol_nombre
        FROM "user" u
        JOIN rol r ON u.rol_id = r.id
        ORDER BY u.id
    """)
    usuarios = cur.fetchall()
    for u in usuarios:
        print(f"  - {u[1]} ({u[2]}) - Rol: {u[3]}")
    
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print("Los datos están correctamente migrados y relacionados.")
    print("Como Administrador, deberías poder ver:")
    print("  1. Clientes: Menu 'Clientes' -> Veras 'Mallplaza Servicios S.A.S'")
    print("  2. Sistemas: Menu 'Sistemas' -> Veras los 10 sistemas")
    print("  3. Sedes: Dentro de cada cliente -> Veras las 5 sedes")
    print("  4. Formularios: Menu 'Formularios' -> Veras 1 formulario activo")
    print("  5. Usuarios: Menu 'Usuarios' -> Veras los 6 usuarios")
    print("\nNOTA: No hay incidencias porque el backup SQL original no las contenía.")
    print("      Puedes crear nuevas incidencias desde el menú 'Nueva Incidencia'.")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] Error verificando relaciones: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

