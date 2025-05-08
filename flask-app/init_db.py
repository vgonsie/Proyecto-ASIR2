import sqlite3

conn = sqlite3.connect("/var/lib/grafana/resultados.db")
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

conn.commit()
conn.close()
print("✔ Base de datos creada en /var/lib/grafana/resultados.db")
