from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import subprocess
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aleatoria'  # Cambia esto en producción!

# Configuración de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Funciones auxiliares ---
def obtener_diccionarios():
    diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios"
    try:
        return [f for f in os.listdir(diccionario_dir) if f.endswith(('.txt', '.lst'))]
    except FileNotFoundError:
        return ["Error: Directorio no encontrado"]

def run_nmap(ip):
    try:
        command = ["nmap", "-sV", ip]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return parse_nmap_output(output.decode("utf-8"))
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
        return parse_hydra_output(output.decode('utf-8'))
    
    except subprocess.CalledProcessError as e:
        error_output = e.output.decode('utf-8')
        return {"error": "Hydra falló", "raw_output": error_output}

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

# --- Configuración de usuarios ---
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Usuario admin (usuario: admin, contraseña: admin)
users = {
    1: User(1, 'admin', generate_password_hash('admin'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# --- Rutas ---
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
    diccionarios = obtener_diccionarios()
    
    if request.method == "POST":
        ip = request.form["ip"]
        if 'nmap' in request.form:
            result = run_nmap(ip)
        elif 'hydra' in request.form:
            diccionario = request.form["diccionario"]
            usuario = request.form["usuario"] or "debian"
            protocolo = request.form["protocolo"]
            hydra_result = run_hydra(ip, diccionario, usuario, protocolo)
    
    return render_template("index.html", 
                         username=current_user.username,
                         result=result, 
                         hydra_result=hydra_result, 
                         diccionarios=diccionarios)

if __name__ == "__main__":
    app.run(debug=True)
