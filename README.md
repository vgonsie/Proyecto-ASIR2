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

### crea-maquina.sh

```bash
#!/bin/bash

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m'

# Rutas
BASE_PROYECTO="$HOME/Proyecto-ASIR2/machines"
ISO_DIR="$BASE_PROYECTO/iso"

# --- Función para mostrar cabeceras ---
show_header() {
    clear
    echo -e "${YELLOW}"
    echo "╔══════════════════════════════════════════╗"
    echo "║   $1"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

# --- Buscar imagen ---
buscar_imagen() {
    show_header "SELECCIONAR TIPO DE INSTALACIÓN"
    echo -e "${BLUE}► ¿Desde qué tipo de archivo quieres crear la máquina?${NC}"
    echo -e "  [1] Archivo ISO\n  [2] Archivo QCOW2"
    echo -en "${BLUE}➤ Opción: ${NC}"
    read tipo_opcion

    if [[ "$tipo_opcion" == "1" ]]; then
        tipo="iso"
    elif [[ "$tipo_opcion" == "2" ]]; then
        tipo="qcow2"
    else
        echo -e "${RED}✖ Opción inválida.${NC}"
        exit 1
    fi

    echo -e "\n${BLUE}Buscando archivos .$tipo en: ${ISO_DIR}${NC}\n"
    mapfile -t ARCHIVOS < <(find "$ISO_DIR" -type f -name "*.$tipo" 2>/dev/null | sort)

    if [ ${#ARCHIVOS[@]} -eq 0 ]; then
        echo -e "${RED}✖ No se encontraron archivos .$tipo.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✔ Archivos disponibles:${NC}\n"
    for i in "${!ARCHIVOS[@]}"; do
        echo "  [$((i+1))] $(basename "${ARCHIVOS[$i]}")"
    done

    while true; do
        echo -en "\n${BLUE}➤ Selecciona un archivo (1-${#ARCHIVOS[@]}): ${NC}"
        read num
        if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le ${#ARCHIVOS[@]} ]; then
            IMG_PATH="${ARCHIVOS[$((num-1))]}"
            break
        else
            echo -e "${RED}✖ Opción inválida.${NC}"
        fi
    done
}

# --- Elegir ubicación ---
elegir_ubicacion() {
    show_header "SELECCIONAR UBICACIÓN"
    echo -e "${BLUE}► ¿Dónde quieres guardar la máquina virtual?${NC}"
    echo -e "  [1] ataque\n  [2] defensa"
    echo -en "${BLUE}➤ Opción: ${NC}"
    read opcion

    case "$opcion" in
        1) VM_DIR="$BASE_PROYECTO/ataque/$VM_NAME" ;;
        2) VM_DIR="$BASE_PROYECTO/defensa/$VM_NAME" ;;
        *) echo -e "${RED}✖ Opción inválida.${NC}"; exit 1 ;;
    esac
}

# --- Selección de hardware ---
seleccionar_recursos() {
    show_header "CONFIGURAR RECURSOS"

    echo -e "${BLUE}► Elige la cantidad de RAM (MB):${NC}"
    echo -e "  [1] 1024 MB\n  [2] 2048 MB\n  [3] 4096 MB"
    echo -en "${BLUE}➤ Opción: ${NC}"
    read ram_opcion
    case "$ram_opcion" in
        1) RAM=1024 ;;
        2) RAM=2048 ;;
        3) RAM=4096 ;;
        *) echo -e "${RED}✖ Opción inválida.${NC}"; exit 1 ;;
    esac

    echo -e "\n${BLUE}► Elige la cantidad de CPUs:${NC}"
    echo -e "  [1] 1 CPU\n  [2] 2 CPUs\n  [3] 4 CPUs\n  [4] 8 CPUs"
    echo -en "${BLUE}➤ Opción: ${NC}"
    read cpu_opcion
    case "$cpu_opcion" in
        1) VCPU=1 ;;
        2) VCPU=2 ;;
        3) VCPU=4 ;;
        4) VCPU=8 ;;
        *) echo -e "${RED}✖ Opción inválida.${NC}"; exit 1 ;;
    esac

    echo -en "\n${BLUE}► Tamaño del disco en GB (ej. 20): ${NC}"
    read DISK_SIZE
    [[ ! "$DISK_SIZE" =~ ^[0-9]+$ ]] && echo -e "${RED}✖ Tamaño no válido.${NC}" && exit 1

    echo -e "\n${BLUE}► Tipo de red:${NC}"
    echo -e "  [1] NAT (default)\n  [2] Bridge (br0)"
    echo -en "${BLUE}➤ Opción: ${NC}"
    read net_opcion
    case "$net_opcion" in
        1) NET_OPT="--network network=default" ;;
        2) NET_OPT="--network bridge=br0" ;;
        *) echo -e "${RED}✖ Opción inválida.${NC}"; exit 1 ;;
    esac
}

# --- Crear la máquina virtual ---
crear_vm() {
    show_header "CREAR MÁQUINA VIRTUAL"

    mkdir -p "$VM_DIR" || {
        echo -e "${RED}✖ Error al crear el directorio $VM_DIR.${NC}"
        exit 1
    }

    DISK_PATH="$VM_DIR/$VM_NAME.qcow2"
    qemu-img create -f qcow2 "$DISK_PATH" "${DISK_SIZE}G"

    echo -e "${YELLOW}⚙️ Creando la máquina virtual...${NC}\n"

    if [[ "$tipo" == "iso" ]]; then
        virt-install \
            --name "$VM_NAME" \
            --ram "$RAM" \
            --vcpus "$VCPU" \
            --disk path="$DISK_PATH",format=qcow2 \
            --os-variant generic \
            $NET_OPT \
            --graphics spice \
            --cdrom "$IMG_PATH" \
            --noautoconsole
    else
        virt-install \
            --name "$VM_NAME" \
            --ram "$RAM" \
            --vcpus "$VCPU" \
            --disk path="$IMG_PATH",format=qcow2 \
            --os-variant generic \
            $NET_OPT \
            --graphics spice \
            --import \
            --noautoconsole
    fi

    echo -e "\n${GREEN}✅ Máquina '$VM_NAME' creada exitosamente.${NC}"
    echo -e "Ubicación: $VM_DIR"
    echo -e "Para iniciar: ${BLUE}virsh start $VM_NAME${NC}"
    echo -e "Para conectarte: ${BLUE}virt-viewer $VM_NAME${NC}\n"
}

# --- Main ---
show_header "CREADOR DE MÁQUINAS VIRTUALES"
echo -en "${BLUE}► Nombre de la máquina virtual: ${NC}"
read VM_NAME
[[ -z "$VM_NAME" ]] && echo -e "${RED}✖ El nombre no puede estar vacío.${NC}" && exit 1

buscar_imagen
elegir_ubicacion
seleccionar_recursos
crear_vm
```
---

He actualizado el script para que:

### 1. Definición de variables y colores
Se definen variables para aplicar colores en los mensajes del terminal (`GREEN`, `RED`, `YELLOW`, `BLUE`, `NC`) y rutas base del proyecto:

- `BASE_PROYECTO="$HOME/Proyecto-ASIR2/machines"`
- `ISO_DIR="$BASE_PROYECTO/iso"`

---

### 2. Cabecera estética
Se ha creado la función `show_header` que limpia la pantalla y muestra una cabecera con bordes y colores llamativos para cada sección del script.

---

### 3. Selección del tipo de instalación
Función: `buscar_imagen`

- Permite elegir si se quiere crear la máquina desde:
  - [1] Archivo `.iso`
  - [2] Archivo `.qcow2`

- Busca en el directorio `~/Proyecto-ASIR2/machines/iso` y muestra los archivos disponibles.
- Guarda la ruta del archivo seleccionado en la variable `IMG_PATH`.

---

### 4. Selección del directorio de destino
Función: `elegir_ubicacion`

- Muestra opciones para elegir dónde se va a guardar la máquina virtual:
  - [1] `ataque`
  - [2] `defensa`

- Se guarda la ruta de destino completa en la variable `VM_DIR`, usando el nombre que introdujo el usuario.

---

### 5. Configuración de hardware
Función: `seleccionar_recursos`

Permite al usuario seleccionar:

- RAM: 1024 MB, 2048 MB, 4096 MB
- vCPU: 1, 2, 4, 8
- Espacio en disco en GB (ingresado manualmente)
- Tipo de red: NAT (default) o Bridge (br0)

---

### 6. Creación de la máquina virtual
Función: `crear_vm`

- Crea el directorio de la máquina virtual dentro de la carpeta correspondiente.
- Si se seleccionó `.iso`:
  - Crea un disco vacío `.qcow2`.
  - Usa `virt-install` con `--cdrom` para instalar desde ISO.
- Si se seleccionó `.qcow2`:
  - Usa `virt-install` con `--import` para cargar la imagen ya instalada.

Muestra un mensaje final con:

- Estado de creación
- Ruta donde quedó almacenada
- Comandos útiles para iniciar y visualizar la máquina:
  - `virsh start <nombre>`
  - `virt-viewer <nombre>`

---

### 7. Flujo principal del script
1. Muestra la cabecera principal del script.
2. Pide el nombre de la nueva máquina virtual.
3. Ejecuta, en orden:
   - `buscar_imagen`
   - `elegir_ubicacion`
   - `seleccionar_recursos`
   - `crear_vm`
