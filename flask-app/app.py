# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import subprocess, os, sqlite3, threading, random, time, smtplib
from scapy.all import sniff, IP, TCP, UDP, send, Ether, ARP
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_aleatoria_segura'
DB_PATH = "/var/lib/grafana/resultados.db"

# ---- LOGIN ----
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

users = {
    1: User(1, 'admin', generate_password_hash('admin'), 'admin'),
    2: User(2, 'user', generate_password_hash('user'), 'user')
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# ---- EMAIL CONFIG ----
EMAIL_FROM = "avisosataquesproyectoasir@gmail.com"
EMAIL_PASS = "hopr tkbe pfse omus"
EMAIL_TO = "avisosataquesproyectoasir@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_alert(tipo, ip):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = f"[ALERTA] Nuevo ataque iniciado"
    body = f"""
    <p>El usuario <strong>{current_user.username}</strong> ha iniciado un ataque <b>{tipo}</b> contra la IP <b>{ip}</b>.</p>
    <p>Fecha y hora: {datetime.now()}</p>
    """
    msg.attach(MIMEText(body, 'html'))
    try:
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.starttls()
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.send_message(msg)
        smtp.quit()
    except Exception as e:
        print(f"[ERROR EMAIL] {e}")

# ---- FUNCIONES COMUNES ----
def obtener_diccionarios():
    d = "/home/kali/Proyecto-ASIR2/diccionarios"
    try:
        return [f for f in os.listdir(d) if f.endswith(('.txt','.lst'))]
    except:
        return []

# ---- NMAP ----
def run_nmap(ip):
    try:
        out = subprocess.check_output(["nmap", "-sV", ip], stderr=subprocess.STDOUT)
        result = parse_nmap_output(out.decode())
        guardar_resultado_nmap(result, ip)
        send_alert("Nmap", ip)
        return result
    except subprocess.CalledProcessError as e:
        return {"error": e.output.decode(), "raw_output": e.output.decode()}

def parse_nmap_output(output):
    data = {"host": "", "status": "", "ports": [], "mac": "", "raw_output": output}
    for line in output.splitlines():
        if "Nmap scan report for" in line:
            data["host"] = line.split("for")[1].strip()
        elif "Host is up" in line:
            data["status"] = line.strip()
        elif "MAC Address:" in line:
            data["mac"] = line.split("MAC Address:")[1].strip()
        elif "/tcp" in line and "open" in line:
            p = line.split()
            data["ports"].append({
                "port": p[0],
                "state": p[1],
                "service": p[2],
                "version": " ".join(p[3:]) if len(p) > 3 else ""
            })
    return data

def guardar_resultado_nmap(result, ip):
    if not result.get("ports"): return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for port in result["ports"]:
            c.execute("INSERT INTO nmap_resultados(ip, puerto, servicio, version) VALUES(?,?,?,?)",
                      (result["host"], port["port"], port["service"], port["version"]))
        c.execute("INSERT INTO ataques_realizados(ip, tipo_ataque) VALUES(?,?)", (ip, "nmap"))
        conn.commit(); conn.close()
    except sqlite3.Error as e:
        print(f"[SQLITE NMAP] {e}")

# ---- HYDRA ----
def run_hydra(ip, dicc, user, proto):
    path = os.path.join("/home/kali/Proyecto-ASIR2/diccionarios", dicc)
    if not os.path.exists(path):
        return {"error": "Diccionario no existe", "raw_output": ""}
    cmd = ["hydra", "-l", user, "-P", path, f"{proto}://{ip}", "-t", "4", "-vV"]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        result = parse_hydra_output(out.decode())
        guardar_resultado_hydra(result, ip)
        send_alert("Hydra", ip)
        return result
    except subprocess.CalledProcessError as e:
        return {"error": "Hydra falló", "raw_output": e.output.decode()}

def parse_hydra_output(output):
    for line in output.splitlines():
        if "login:" in line and "password:" in line:
            parts = line.split()
            return {
                "host": parts[parts.index("host:")+1],
                "port": parts[0].strip("[]"),
                "login": parts[parts.index("login:")+1],
                "password": parts[parts.index("password:")+1],
                "raw_output": output
            }
    return {"error": "No credenciales", "raw_output": output}

def guardar_resultado_hydra(result, ip):
    if result.get("error"): return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO hydra_resultados(ip, puerto, usuario, password, protocolo) VALUES(?,?,?,?,?)",
                  (result["host"], result["port"], result["login"], result["password"], "ssh"))
        c.execute("INSERT INTO ataques_realizados(ip, tipo_ataque, puerto) VALUES(?,?,?)",
                  (ip, "hydra", result["port"]))
        conn.commit(); conn.close()
    except sqlite3.Error as e:
        print(f"[SQLITE HYDRA] {e}")

# ---- FLASK ROUTES ----
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
    if request.method == "POST":
        ip = request.form["ip"]
        tipo = request.form["tipo_ataque"]
        if tipo == "nmap":
            result = run_nmap(ip)
        elif tipo == "hydra" and current_user.role == "admin":
            dicc = request.form["diccionario"]
            usuario = request.form["usuario"]
            proto = request.form["protocolo"]
            hydra_result = run_hydra(ip, dicc, usuario, proto)

    return render_template(
        "index.html",
        username=current_user.username,
        role=current_user.role,
        result=result,
        hydra_result=hydra_result,
        diccionarios=obtener_diccionarios(),
    )

if __name__ == "__main__":
    app.run(debug=True)
