# init_db.py
import sqlite3

DB_PATH = "/var/lib/grafana/resultados.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Tabla Nmap
c.execute('''
CREATE TABLE IF NOT EXISTS nmap_resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    puerto TEXT,
    servicio TEXT,
    version TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Tabla Hydra
c.execute('''
CREATE TABLE IF NOT EXISTS hydra_resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    puerto TEXT,
    usuario TEXT,
    password TEXT,
    protocolo TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Tabla de ataques realizados
c.execute('''
CREATE TABLE IF NOT EXISTS ataques_realizados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    tipo_ataque TEXT,
    puerto TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Tabla para resultados de sniffing
c.execute('''
CREATE TABLE IF NOT EXISTS sniffing_resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_ip TEXT,
    dst_ip TEXT,
    protocolo TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Tabla para escaneo SSH
c.execute('''
CREATE TABLE IF NOT EXISTS ssh_resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT,
    salida TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print(f"✔ Base de datos creada/actualizada en {DB_PATH}")
