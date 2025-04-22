import subprocess

def obtener_ip():
    # Pide la IP al usuario
    ip = input("Introduce la IP o rango de red que deseas escanear (Ejemplo: 192.168.1.1 o 192.168.1.0/24): ")
    return ip

def ejecutar_nmap(ip):
    # Ejecuta Nmap con el comando de escaneo completo de la red
    print(f"\nEscaneando la IP: {ip}")
    
    # Comando Nmap
    comando = ["nmap", "-A", ip]
    
    try:
        # Ejecuta el comando Nmap y captura la salida
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Muestra el resultado del escaneo
        print("\nResultado del escaneo:\n")
        print(resultado.stdout)
        
    except Exception as e:
        print(f"Error al ejecutar Nmap: {e}")

def main():
    # Paso 1: Obtener la IP de la red que quiere escanear el usuario
    ip = obtener_ip()
    
    # Paso 2: Ejecutar el escaneo con Nmap
    ejecutar_nmap(ip)

if __name__ == "__main__":
    main()
