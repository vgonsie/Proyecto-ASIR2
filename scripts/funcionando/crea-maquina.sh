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

