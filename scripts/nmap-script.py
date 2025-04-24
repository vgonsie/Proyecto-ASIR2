import sys
import subprocess

def ejecutar_nmap(ip):
    # Ejecuta Nmap con el comando de escaneo completo de la red
    print(f"\nEscaneando la IP: {ip}")
    
    # Comando Nmap
    comando = ["nmap", "-A", ip]
    
    try:
        # Ejecuta el comando Nmap y captura la salida
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Devuelve el resultado del escaneo
        return resultado.stdout
        
    except Exception as e:
        return f"Error al ejecutar Nmap: {e}"

if __name__ == "__main__":
    # Obtener la IP desde los argumentos
    ip = sys.argv[1] if len(sys.argv) > 1 else None
    
    if ip:
        resultado = ejecutar_nmap(ip)
        print(resultado)
    else:
        print("No se proporcionó una IP para escanear.")
