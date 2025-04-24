from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        ip = request.form["ip"]  # Obtener la IP desde el formulario
        result = run_nmap(ip)  # Ejecutar Nmap
    return render_template("index.html", result=result)

def run_nmap(ip):
    try:
        # Ejecutar el comando nmap en la terminal y capturar la salida
        command = ["nmap", ip]
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return parse_nmap_output(result.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar Nmap: {e.output.decode('utf-8')}"

def parse_nmap_output(output):
    """
    Procesa la salida de Nmap para hacerla más legible.
    """
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

if __name__ == "__main__":
    app.run(debug=True)
