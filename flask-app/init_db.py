# init_db.py
import sqlite3

# Crear conexión
conn = sqlite3.connect("resultados.db")
c = conn.cursor()

# Crear tabla para resultados de Nmap
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

# Crear tabla para resultados de Hydra
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

conn.commit()
conn.close()
print("✔ Base de datos creada con éxito (resultados.db)")
