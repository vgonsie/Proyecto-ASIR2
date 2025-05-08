from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import subprocess
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configurar logging detallado
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'clave_secreta_aleatoria_segura'

# Ruta corregida: accesible por Grafana
DB_PATH = "/var/lib/grafana/resultados.db"

# Configuración de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Definir la clase User antes de usarla
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Usuarios simulados (puedes cambiar la contraseña aquí)
users = {
    1: User(1, 'admin', generate_password_hash('admin'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

def obtener_diccionarios():
    diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios"
    try:
        return [f for f in os.listdir(diccionario_dir) if f.endswith(('.txt', '.lst'))]
    except FileNotFoundError:
        logger.error("Directorio de diccionarios no encontrado")
        return ["Error: Directorio no encontrado"]

# Escaneo Nmap
def run_nmap(ip):
    try:
        logger.debug(f"Ejecutando Nmap contra {ip}")
        command = ["nmap", "-sV", ip]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = parse_nmap_output(output.decode("utf-8"))
        guardar_resultado_nmap(result)
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar Nmap: {e.output.decode('utf-8')}")
        return {"error": f"Error en Nmap: {e.output.decode('utf-8')}", "raw_output": e.output.decode("utf-8")}

def parse_nmap_output(output):
    data = {
        "host": "",
        "status": "",
        "ports": [],
        "mac": "",
        "raw_output": output
    }

    for line in output.splitlines():
        if "Nmap scan report for" in line:
            data["host"] = line.split("for")[1].strip()
        elif "Host is up" in line:
            data["status"] = line.strip()
        elif "MAC Address:" in line:
            data["mac"] = line.split("MAC Address:")[1].strip()
        elif "/tcp" in line and "open" in line:
            parts = [p for p in line.split() if p]
            if len(parts) >= 4:
                data["ports"].append({
                    "port": parts[0],
                    "state": parts[1],
                    "service": parts[2],
                    "version": " ".join(parts[3:]) if len(parts) > 3 else ""
                })
    return data

# Ataque con Hydra
def run_hydra(ip, diccionario, usuario, protocolo):
    try:
        logger.debug(f"Ejecutando Hydra contra {ip} con diccionario {diccionario}")
        diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios/"
        diccionario_path = os.path.join(diccionario_dir, diccionario)

        if not os.path.exists(diccionario_path):
            logger.warning(f"El diccionario {diccionario_path} no existe")
            return {"error": f"El diccionario {diccionario} no existe", "raw_output": ""}

        command = [
            "hydra",
            "-l", usuario,
            "-P", diccionario_path,
            f"{protocolo}://{ip}",
            "-t", "4",
            "-vV"
        ]

        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = parse_hydra_output(output.decode('utf-8'))
        guardar_resultado_hydra(result)
        return result

    except subprocess.CalledProcessError as e:
        logger.error(f"Hydra falló: {e.output.decode('utf-8')}")
        return {"error": "Hydra falló", "raw_output": e.output.decode('utf-8')}

def parse_hydra_output(output):
    for line in output.splitlines():
        if "host:" in line and "login:" in line and "password:" in line:
            parts = line.split()
            return {
                "port": parts[0].replace("[", "").replace("]", ""),
                "host": parts[parts.index("host:")+1],
                "login": parts[parts.index("login:")+1],
                "password": parts[parts.index("password:")+1],
                "raw_output": output
            }
    return {"error": "No se encontraron credenciales válidas", "raw_output": output}

# Guardar en SQLite
def guardar_resultado_nmap(result):
    logger.debug(f"Intentando guardar resultado de Nmap: {result}")
    if "ports" not in result:
        logger.warning("No hay puertos abiertos para guardar")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        logger.debug("✅ Conexión exitosa a la base de datos")
        c = conn.cursor()
        for port in result["ports"]:
            c.execute('''
                INSERT INTO nmap_resultados (ip, puerto, servicio, version)
                VALUES (?, ?, ?, ?)
            ''', (
                result["host"],
                port["port"],
                port["service"],
                port["version"]
            ))
        conn.commit()
        logger.info("✅ Datos de Nmap guardados correctamente")
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"[ERROR SQLITE - NMAP] {e}")

def guardar_resultado_hydra(result):
    logger.debug(f"Intentando guardar resultado de Hydra: {result}")
    if "error" in result:
        logger.warning("Resultado de Hydra contiene errores. No se guardará.")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        logger.debug("✅ Conexión exitosa a la base de datos")
        c = conn.cursor()
        c.execute('''
            INSERT INTO hydra_resultados (ip, puerto, usuario, password, protocolo)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            result["host"],
            result["port"],
            result["login"],
            result["password"],
            "ssh"
        ))
        conn.commit()
        logger.info("✅ Datos de Hydra guardados correctamente")
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"[ERROR SQLITE - HYDRA] {e}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users.values() if u.username == username), None)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        logger.warning("Inicio de sesión fallido para usuario: {}".format(username))
        return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    result = None
    hydra_result = None
    diccionarios = obtener_diccionarios()

    if request.method == "POST":
        ip = request.form["ip"]
        if 'nmap' in request.form:
            logger.info(f"Iniciando escaneo Nmap en IP: {ip}")
            result = run_nmap(ip)
        elif 'hydra' in request.form:
            diccionario = request.form["diccionario"]
            usuario = request.form["usuario"] or "debian"
            protocolo = request.form["protocolo"]
            logger.info(f"Iniciando ataque Hydra en {ip} con {diccionario}, usuario {usuario}, protocolo {protocolo}")
            hydra_result = run_hydra(ip, diccionario, usuario, protocolo)

    return render_template("index.html",
                           username=current_user.username,
                           result=result,
                           hydra_result=hydra_result,
                           diccionarios=diccionarios)

if __name__ == "__main__":
    # Prueba inicial de conexión a la base de datos
    try:
        logger.debug(f"Verificando conexión a la base de datos: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        logger.info("✅ Conexión a la base de datos verificada correctamente")
        conn.close()
    except Exception as e:
        logger.error(f"❌ No se pudo conectar a la base de datos: {e}")
    
    app.run(debug=False)
