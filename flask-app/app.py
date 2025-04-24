from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
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
    
    return render_template("index.html", result=result, hydra_result=hydra_result, diccionarios=diccionarios)

def run_nmap(ip):
    try:
        command = ["nmap", ip]
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return parse_nmap_output(result.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar Nmap: {e.output.decode('utf-8')}"

def parse_nmap_output(output):
    parsed_result = []
    lines = output.splitlines()

    for line in lines:
        if "open" in line:
            parsed_result.append(f"<span class='open-port'>{line}</span>")
        elif "Host is up" in line:
            parsed_result.append(f"<span class='host-status'>{line}</span>")
        elif "Nmap scan report" in line:
            parsed_result.append(f"<span class='scan-report'>{line}</span>")
        elif "MAC Address" in line:
            parsed_result.append(f"<span class='mac-address'>{line}</span>")
        elif "OS" in line:
            parsed_result.append(f"<span class='os-info'>{line}</span>")
        else:
            parsed_result.append(line)
    
    return "<br>".join(parsed_result)

def run_hydra(ip, diccionario, usuario, protocolo):
    try:
        diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios/"
        diccionario_path = os.path.join(diccionario_dir, diccionario)
        
        if not os.path.exists(diccionario_path):
            return {"error": f"El diccionario {diccionario} no se encuentra"}
        
        command = [
            "hydra",
            "-l", usuario,
            "-P", diccionario_path,
            f"{protocolo}://{ip}"
        ]
        
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return extract_relevant_info(result.decode('utf-8'))
    
    except subprocess.CalledProcessError as e:
        error_output = e.output.decode('utf-8')
        if "0 valid passwords found" in error_output:
            return {"error": "No se encontraron contraseñas válidas"}
        else:
            return {"error": f"Error en Hydra: {error_output}"}

def extract_relevant_info(output):
    lines = output.splitlines()
    for line in lines:
        if "host:" in line and "login:" in line and "password:" in line:
            parts = line.split()
            port = parts[0].replace("[", "").replace("]", "")
            host = parts[parts.index("host:")+1]
            login = parts[parts.index("login:")+1]
            password = parts[parts.index("password:")+1]
            
            return {
                "port": port,
                "host": host,
                "login": login,
                "password": password,
                "raw_output": line  # Guardamos también el output original
            }
    
    # Si no encontró credenciales válidas, devolver el output completo
    return {"error": "No se encontraron credenciales válidas", "raw_output": output}

def obtener_diccionarios():
    diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios"
    try:
        archivos = [f for f in os.listdir(diccionario_dir) if f.endswith(('.txt', '.lst'))]
        return archivos
    except FileNotFoundError:
        return ["No se encontró el directorio de diccionarios"]

if __name__ == "__main__":
    app.run(debug=True)
