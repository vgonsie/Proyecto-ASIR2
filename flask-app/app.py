from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    hydra_result = ""
    diccionarios = obtener_diccionarios()  # Obtener lista de diccionarios disponibles
    
    if request.method == "POST":
        ip = request.form["ip"]  # Obtener la IP desde el formulario
        
        if 'nmap' in request.form:  # Ejecutar Nmap
            result = run_nmap(ip)
        elif 'hydra' in request.form:  # Ejecutar Hydra
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
        # Especificamos la ruta completa del diccionario
        diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios/"
        diccionario_path = os.path.join(diccionario_dir, diccionario)
        
        # Comprobamos si el archivo existe
        if not os.path.exists(diccionario_path):
            return f"Error: El diccionario {diccionario} no se encuentra en {diccionario_dir}."
        
        # Ejecutar el comando de Hydra
        command = [
            "hydra",
            "-l", usuario,
            "-P", diccionario_path,  # Usamos la ruta completa del diccionario
            f"{protocolo}://{ip}"
        ]
        
        # Captura tanto la salida estándar como la de error
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        
        # Extraer solo la información relevante (host, login, password)
        return extract_relevant_info(result.decode('utf-8'))
    
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar Hydra: {e.output.decode('utf-8')}"

def extract_relevant_info(output):
    # Filtrar solo las líneas relevantes con la información de los intentos
    lines = output.splitlines()
    relevant_lines = []

    for line in lines:
        if "[ssh]" in line:  # Solo mostrar los intentos de SSH
            relevant_lines.append(line.strip())

    return "<br>".join(relevant_lines)

def obtener_diccionarios():
    diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios"
    archivos = [f for f in os.listdir(diccionario_dir) if f.endswith('.txt') or f.endswith('.lst')]
    return archivos

if __name__ == "__main__":
    app.run(debug=True)
