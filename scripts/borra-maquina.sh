#!/bin/bash

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ATAQUE_DIR="$HOME/Proyecto-ASIR2/machines/ataque"
DEFENSA_DIR="$HOME/Proyecto-ASIR2/machines/defensa"

# Cabecera
show_header() {
    clear
    echo -e "${YELLOW}"
    echo "╔════════════════════════════════════════╗"
    echo "║     ELIMINADOR DE MÁQUINAS VIRT-MGR    ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Seleccionar tipo de máquina
select_machine_type() {
    show_header
    echo "¿Qué tipo de máquina quieres eliminar?"
    echo "1) Ataque"
    echo "2) Defensa"
    read -p "Opción [1/2]: " tipo

    case "$tipo" in
        2) DIR="$DEFENSA_DIR" ;;
        1) DIR="$ATAQUE_DIR" ;;
        *) echo -e "${RED}Opción no válida. Saliendo...${NC}"; exit 1 ;;
    esac

    if [ ! -d "$DIR" ]; then
        echo -e "${RED}Directorio no encontrado: $DIR${NC}"
        exit 1
    fi
}

# Seleccionar máquina
select_machine() {
    show_header
    echo -e "Máquinas disponibles en: ${GREEN}$DIR${NC}"
    echo "----------------------------------------"

    machines=()
    while IFS= read -r dir; do
        machines+=("$(basename "$dir")")
    done < <(find "$DIR" -mindepth 1 -maxdepth 1 -type d | sort)

    if [ ${#machines[@]} -eq 0 ]; then
        echo -e "${RED}No hay máquinas disponibles para eliminar.${NC}"
        exit 1
    fi

    for i in "${!machines[@]}"; do
        echo "$((i+1))) ${machines[$i]}"
    done

    read -p "Selecciona una máquina [1-${#machines[@]}]: " choice
    if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "${#machines[@]}" ]; then
        echo -e "${RED}Selección no válida. Saliendo...${NC}"
        exit 1
    fi

    MACHINE_FOLDER="${machines[$((choice-1))]}"
    MACHINE_PATH="$DIR/$MACHINE_FOLDER"
}

# Buscar nombre de la máquina
find_machine_file() {
    QCOW2_FILE=$(find "$MACHINE_PATH" -type f -name "*.qcow2")

    if [[ -z "$QCOW2_FILE" ]]; then
        echo -e "${RED}No se encontró un archivo .qcow2 en $MACHINE_PATH.${NC}"
        exit 1
    fi

    MACHINE_NAME=$(basename "$QCOW2_FILE" .qcow2)
}

# Confirmación
confirm_deletion() {
    show_header
    echo -e "${YELLOW}Resumen de eliminación:${NC}"
    echo "----------------------------------------"
    echo -e "Nombre máquina: ${GREEN}$MACHINE_NAME${NC}"
    echo -e "Ruta completa:  ${GREEN}$MACHINE_PATH${NC}"
    echo "----------------------------------------"

    read -p "¿Estás seguro de que quieres eliminarla? [s/N]: " confirm
    if [[ ! "$confirm" =~ ^[sS]$ ]]; then
        echo -e "${YELLOW}Operación cancelada.${NC}"
        exit 0
    fi
}

# Eliminar con virsh y del disco
delete_machine() {
    echo -e "${YELLOW}Eliminando desde virt-manager...${NC}"
    virsh destroy "$MACHINE_NAME" 2>/dev/null
    virsh undefine "$MACHINE_NAME" --remove-all-storage --nvram 2>/dev/null

    if virsh list --all | grep -q "$MACHINE_NAME"; then
        echo -e "${RED}La máquina aún aparece en virt-manager. Revisa manualmente.${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Eliminando carpeta...${NC}"
    rm -rf "$MACHINE_PATH"
    echo -e "${GREEN}✔ Máquina $MACHINE_NAME eliminada correctamente.${NC}"
}

# Ejecución
select_machine_type
select_machine
find_machine_file
confirm_deletion
delete_machine

exit 0

