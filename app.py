# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
import subprocess
import os
import sqlite3
from scapy.all import sniff, IP, TCP, UDP, send, Ether, ARP
from werkzeug.security import generate_password_hash, check_password_hash
import threading, random, time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'clave_secreta_aleatoria_segura'

# Ruta a la DB
DB_PATH = "/var/lib/grafana/resultados.db"

# Configuración Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Usuarios ---
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Usuario demo
users = {
    1: User(1, 'admin', generate_password_hash('admin'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# --- Funciones de correo ---
EMAIL_FROM = "avisosataquesproyectoasir@gmail.com"
EMAIL_PASS = "pe12pe34"
EMAIL_TO   = "avisosataquesproyectoasir@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587

def send_alert(subject, body):
    """Envía un correo con asunto y cuerpo HTML/text."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To']   = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    try:
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.starttls()
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.send_message(msg)
        smtp.quit()
    except Exception as e:
        print(f"[ERROR EMAIL] {e}")

# --- Diccionarios ---
def obtener_diccionarios():
    d = "/home/kali/Proyecto-ASIR2/diccionarios"
    try:
        return [f for f in os.listdir(d) if f.endswith(('.txt','.lst'))]
    except:
        return []

# --- Nmap ---
def run_nmap(ip):
    try:
        out = subprocess.check_output(["nmap","-sV",ip], stderr=subprocess.STDOUT)
        res = parse_nmap_output(out.decode())
        guardar_resultado_nmap(res, ip)
        return res
    except subprocess.CalledProcessError as e:
        return {"error": e.output.decode(), "raw_output": e.output.decode()}

def parse_nmap_output(output):
    data = {"host":"","status":"","ports":[],"mac":"","raw_output":output}
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
                "version": " ".join(p[3:]) if len(p)>3 else ""
            })
    return data

def guardar_resultado_nmap(result, ip):
    if not result.get("ports"): return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for port in result["ports"]:
            c.execute(
                "INSERT INTO nmap_resultados(ip, puerto, servicio, version) VALUES(?,?,?,?)",
                (result["host"], port["port"], port["service"], port["version"])
            )
            # ALERTA por correo si encontramos SSH(22) o FTP(21) abierto
            if port["port"].startswith("22/tcp") or port["port"].startswith("21/tcp"):
                subj = f"[ALERTA] Puerto {port['port']} abierto en {ip}"
                body = f"""
                <p><strong>Nmap detectó puerto abierto:</strong></p>
                <ul>
                  <li>Host: {result['host']}</li>
                  <li>Puerto: {port['port']}</li>
                  <li>Servicio: {port['service']}</li>
                  <li>Versión: {port['version']}</li>
                  <li>Fecha: {datetime.now()}</li>
                </ul>
                """
                send_alert(subj, body)
        c.execute(
            "INSERT INTO ataques_realizados(ip, tipo_ataque) VALUES(?,?)",
            (ip, "nmap")
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[SQLITE NMAP] {e}")

# --- Hydra ---
def run_hydra(ip, dicc, user, proto):
    path = os.path.join("/home/kali/Proyecto-ASIR2/diccionarios", dicc)
    if not os.path.exists(path):
        return {"error":"Diccionario no existe","raw_output":""}
    cmd = ["hydra","-l",user,"-P",path,f"{proto}://{ip}","-t","4","-vV"]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        res = parse_hydra_output(out.decode())
        guardar_resultado_hydra(res, ip)
        return res
    except subprocess.CalledProcessError as e:
        return {"error":"Hydra falló","raw_output":e.output.decode()}

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
    return {"error":"No credenciales","raw_output":output}

def guardar_resultado_hydra(res, ip):
    if res.get("error"): return
    try:
        conn = sqlite3.connect(DB_PATH); c=conn.cursor()
        c.execute(
            "INSERT INTO hydra_resultados(ip, puerto, usuario, password, protocolo) VALUES(?,?,?,?,?)",
            (res["host"], res["port"], res["login"], res["password"], "ssh")
        )
        c.execute(
            "INSERT INTO ataques_realizados(ip, tipo_ataque, puerto) VALUES(?,?,?)",
            (ip, "hydra", res["port"])
        )
        conn.commit(); conn.close()
        # Alerta por credenciales válidas
        subj = f"[ALERTA] Credenciales encontradas en {ip}"
        body = f"""
          <p><strong>Hydra obtuvo credenciales válidas:</strong></p>
          <ul>
            <li>Host: {res['host']}</li>
            <li>Puerto: {res['port']}</li>
            <li>Usuario: {res['login']}</li>
            <li>Contraseña: {res['password']}</li>
            <li>Fecha: {datetime.now()}</li>
          </ul>
        """
        send_alert(subj, body)
    except sqlite3.Error as e:
        print(f"[SQLITE HYDRA] {e}")

# --- Rutas Flask ---
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form['username']; p=request.form['password']
        user = next((x for x in users.values() if x.username==u),None)
        if user and check_password_hash(user.password_hash,p):
            login_user(user); return redirect(url_for('index'))
        return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('login'))

@app.route('/', methods=['GET','POST'])
@login_required
def index():
    result=None; hydra_result=None; message=None
    if request.method=='POST':
        ip = request.form['ip']
        tipo = request.form['tipo_ataque']
        if tipo=='nmap':
            result = run_nmap(ip)
        elif tipo=='hydra':
            hydra_result = run_hydra(
                ip,
                request.form['diccionario'],
                request.form['usuario'] or 'debian',
                request.form['protocolo']
            )
    return render_template(
        'index.html',
        username=current_user.username,
        result=result,
        hydra_result=hydra_result,
        diccionarios=obtener_diccionarios(),
        interfaz_list=[],
        interfaz_predicha=None,
        sniff_result=None,
        ssh_ipa_result=None,
        message=message
    )

if __name__=='__main__':
    app.run(debug=True)
