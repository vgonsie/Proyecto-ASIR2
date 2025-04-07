# Simulación Automática de Ataques y Respuesta con Python

**Autor:** Vicente González Sierra  
**Tutor:** Francisco Ávila  

**Centro Educativo:** I.E.S Francisco Romero Vargas (Jerez de la Frontera)  
**Ciclo Formativo:** Administración de Sistemas Informáticos en Red (ASIR)  
**Curso:** 2024/2025  

---

## 1. Introducción  
Este proyecto tiene como objetivo desarrollar un sistema automatizado que simule ataques informáticos y analice las respuestas de los mecanismos de defensa, como firewalls, Fail2Ban y sistemas SIEM (Wazuh).  

El sistema permitirá realizar pruebas de seguridad controladas para evaluar la efectividad de las medidas implementadas y mejorar la protección de la infraestructura.  

---

## 2. Finalidad  
El proyecto servirá para:  
- Evaluar la respuesta de sistemas de seguridad ante ataques simulados.  
- Automatizar la simulación de ataques como escaneos de puertos, ataques de fuerza bruta y DoS.  
- Ayudar a detectar vulnerabilidades y mejorar la seguridad.  
- Generar reportes detallados y alertas en tiempo real sobre los eventos de seguridad.  

---

## 3. Objetivos  
Los objetivos principales de este proyecto son:  
- Implementar un script en **Python** que realice escaneos de puertos con **Nmap**.  
- Desarrollar ataques simulados de **fuerza bruta** y **DoS** en un entorno controlado.  
- Analizar los registros de seguridad para evaluar la respuesta de **Fail2Ban** y **Wazuh**.  
- Crear un **panel de control web** con **Flask** y **Grafana** para la visualización de eventos.  
- Configurar un sistema de **alertas en Telegram o correo electrónico** ante incidentes detectados.  

---

## 4. Medios Necesarios  

### **Hardware:**  
- Máquina virtual con **Linux** para ejecutar las pruebas.  
- Red local configurada para las simulaciones.  

### **Software:**  
- **Python** para la automatización de ataques.  
- **Nmap** y **Scapy** para el análisis de red.  
- **Fail2Ban** y **Wazuh** para la detección y respuesta a ataques.  
- **Flask** y **Grafana** para la visualización de eventos.  
- **Docker** para ejecutar entornos aislados.  
- **API de Telegram** o servidor de correo para notificaciones.  

---

## 5. Planificación  

| **Tarea** | **Tiempo estimado** |
|------------------------------|----------------|
| Instalación y configuración del entorno | 5 horas |
| Desarrollo del escaneo de puertos con Nmap | 4 horas |
| Implementación de ataques de fuerza bruta | 6 horas |
| Simulación de ataque DoS con Python | 5 horas |
| Integración con Fail2Ban y Wazuh | 6 horas |
| Creación del panel de control con Flask y Grafana | 8 horas |
| Configuración de alertas en Telegram/correo | 4 horas |
| Pruebas de seguridad y ajustes | 7 horas |
| Documentación del proyecto | 6 horas |
| **Total estimado:** | **51 horas** |

---

## Creación de primeros scripts (outdated)

### 1. `CreaAtaque1.sh`

Este script se utiliza para crear la máquina virtual **ataque1** en KVM utilizando la herramienta `virt-install`. Configura la VM con 2 GB de RAM, 2 vCPUs y un disco de 10 GB, e instala una imagen de Ubuntu 22.04.
  ```bash
  virt-install --name ataque1 \
  --ram 2048 --vcpus 2 \
  --disk path=/var/lib/libvirt/images/ataque1.qcow2,size=10 \
  --os-type linux --os-variant ubuntu22.04 \
  --network bridge=virbr0 \
  --cdrom /var/lib/libvirt/boot/ubuntu.iso \
  --graphics none --console pty,target_type=serial
  ```

### **Uso**:

1. Descargar la versión Ubuntu 24.04.
  ```bash
  wget https://releases.ubuntu.com/22.04/ubuntu-22.04.4-live-server-amd64.iso -O ubuntu-22.04.iso
  ```

2. Para poder ejecutar el script, primero debes dar permisos de ejecución con el siguiente comando:
  ```bash
  chmod +x ./lab/CreaAtaque1.sh
  ```
3. Ejecuta el siguiente comando en la terminal:
   ```bash
   ./lab/CreaAtaque1.sh
   ```

---

### 2. `BorraAtaque1.sh`

Este script elimina la máquina virtual **ataque1** y borra su disco asociado. Utiliza `virsh` para detener y eliminar la máquina, asegurando que no queden restos de la VM en el sistema.
  ```bash
  virsh destroy ataque1
  virsh undefine ataque1
  rm -f /var/lib/libvirt/images/ataque1.qcow2
  ```

#### **Uso**

Para poder ejecutar el script, primero debes dar permisos de ejecución con el siguiente comando:
  ```bash
  chmod +x ./lab/BorraAtaque1.sh
  ```

Ejecuta el siguiente comando:
  ```bash
  ./lab/BorraAtaque1.sh
  ```

---

### Búsqueda sobre máquinas vulnerables y automatización

### Metasploitable

Metasploitable 2 es una máquina vulnerable con fallos en SSH, FTP, MySQL y Samba, credenciales débiles, inyección SQL y ejecución remota de código. Es ideal para pruebas de penetración y análisis de seguridad.

### Login

Usuario: "msfadmin" <br>
Contraseña: "msfadmin"

Descargar [Metasploitable](https://sourceforge.net/projects/metasploitable/)

### Conversión a qcow2 y automatización de la instalación de máquinas vulnerables (SIN TERMINAR)

  ```bash
  #!/bin/bash

VM_NAME="Metasploitable2"
VMDK_PATH="/ruta/al/archivo/Metasploitable.vmdk"
QCOW2_PATH="/var/lib/libvirt/images/Metasploitable2.qcow2"
ISO_PATH="/usr/share/virtio-win/virtio-win.iso"

function instalar_vm() {
    echo "Convirtiendo VMDK a QCOW2..."
    qemu-img convert -f vmdk -O qcow2 "$VMDK_PATH" "$QCOW2_PATH"
    
    echo "Creando máquina virtual en KVM..."
    virt-install \
        --name "$VM_NAME" \
        --ram 1024 --vcpus 1 \
        --disk path="$QCOW2_PATH",format=qcow2 \
        --os-type linux --os-variant generic \
        --network network=default,model=virtio \
        --graphics none \
        --console pty,target_type=serial \
        --import
    
    echo "Instalación completada. Usa 'virsh list --all' para verificar."
}

function eliminar_vm() {
    echo "Eliminando la máquina virtual..."
    virsh destroy "$VM_NAME"
    virsh undefine "$VM_NAME"
    rm -f "$QCOW2_PATH"
    echo "Máquina eliminada correctamente."
}

case "$1" in
    instalar)
        instalar_vm
        ;;
    eliminar)
        eliminar_vm
        ;;
    *)
        echo "Uso: $0 {instalar|eliminar}"
        exit 1
        ;;
esac
  ```

### Permisos 

  ```bash
  chmod +x ./Defensa1.sh
  ```

### Actualización de script para conversión a qcow2 y automatización de creación y borrado de máquinas vulnerables.

He actualizado el script para que solicite por pantalla al usuario los datos para la creación y borrado de la VM con las diferentes opciones.

  ```bash
#!/bin/bash

function mostrar_menu() {
  echo "Selecciona una opción:"
  echo "1) Instalar máquina virtual"
  echo "2) Eliminar máquina virtual"
  echo "3) Salir"
}

function solicitar_valores() {
  echo "Configuración de la máquina virtual:"
  
  # Opciones predefinidas para el nombre de la VM
  declare -A nombres_vm=(
    [1]="Metasploitable2"
    [2]="KaliLinux"
    [3]="UbuntuServer"
  )
  echo "Elige un nombre para la máquina virtual:"
  for key in "${!nombres_vm[@]}"; do
    echo "$key) ${nombres_vm[$key]}"
  done
  read -p "Opción (1-${#nombres_vm[@]}): " opcion_nombre
  VM_NAME=${nombres_vm[$opcion_nombre]}

  # Opciones predefinidas para la ruta del VMDK
  declare -A rutas_vmdk=(
    [1]="/ruta/al/archivo/Metasploitable.vmdk"
    [2]="/ruta/al/archivo/KaliLinux.vmdk"
    [3]="/ruta/al/archivo/UbuntuServer.vmdk"
  )
  echo "Elige la ruta del archivo VMDK:"
  for key in "${!rutas_vmdk[@]}"; do
    echo "$key) ${rutas_vmdk[$key]}"
  done
  read -p "Opción (1-${#rutas_vmdk[@]}): " opcion_vmdk
  VMDK_PATH=${rutas_vmdk[$opcion_vmdk]}

  # Ruta predefinida para el archivo QCOW2
  QCOW2_PATH="/var/lib/libvirt/images/${VM_NAME}.qcow2"

  # Opciones predefinidas para la RAM
  declare -A opciones_ram=(
    [1]=1024
    [2]=2048
    [3]=4096
  )
  echo "Elige la cantidad de RAM (en MB):"
  for key in "${!opciones_ram[@]}"; do
    echo "$key) ${opciones_ram[$key]} MB"
  done
  read -p "Opción (1-${#opciones_ram[@]}): " opcion_ram
  RAM=${opciones_ram[$opcion_ram]}

  # Opciones predefinidas para el número de vCPUs
  declare -A opciones_vcpus=(
    [1]=1
    [2]=2
    [3]=4
  )
  echo "Elige el número de vCPUs:"
  for key in "${!opciones_vcpus[@]}"; do
    echo "$key) ${opciones_vcpus[$key]} vCPU(s)"
  done
  read -p "Opción (1-${#opciones_vcpus[@]}): " opcion_vcpus
  VCPUS=${opciones_vcpus[$opcion_vcpus]}
}

function instalar_vm() {
  echo "Convirtiendo VMDK a QCOW2..."
  qemu-img convert -f vmdk -O qcow2 "$VMDK_PATH" "$QCOW2_PATH"
  
  echo "Creando máquina virtual en KVM..."
  virt-install \
      --name "$VM_NAME" \
      --ram "$RAM" --vcpus "$VCPUS" \
      --disk path="$QCOW2_PATH",format=qcow2 \
      --os-type linux --os-variant generic \
      --network network=default,model=virtio \
      --graphics none \
      --console pty,target_type=serial \
      --import
  
  echo "Instalación completada. Usa 'virsh list --all' para verificar."
}

function eliminar_vm() {
  echo "Eliminando la máquina virtual..."
  virsh destroy "$VM_NAME"
  virsh undefine "$VM_NAME"
  rm -f "$QCOW2_PATH"
  echo "Máquina eliminada correctamente."
}

while true; do
  mostrar_menu
  read -p "Opción (1-3): " opcion_principal

  case "$opcion_principal" in
    1)
      solicitar_valores
      instalar_vm
      ;;
    2)
      solicitar_valores
      eliminar_vm
      ;;
    3)
      echo "Saliendo..."
      exit 0
      ;;
    *)
      echo "Opción no válida. Inténtalo de nuevo."
      ;;
  esac
done
  ```

---

### Script para escanear red en busca de puertos abiertos con Nmap

Este script servirá para escanear una red en busca de puertos abiertos para explotar una vulnerabilidad en una máquina.

  ```bash
#!/bin/bash

if [ -z "$1" ]; then
  echo "Uso: $0 <dirección_ip_o_host>"
  exit 1
fi

TARGET=$1

echo "Escaneando puertos abiertos de: $TARGET"

nmap -p- --open $TARGET
  ```

### Dar permisos al script

  ```bash
chmod +x scan_ports.sh
  ```

### Ejecutar el script

  ```bash
./scan_ports.sh 192.168.1.1
  ```

---

### ACTUALIZACIÓN DE TODOS LOS SCRIPTS

