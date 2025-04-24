#!/bin/bash

# Script para convertir imágenes de máquinas virtuales a formato QCOW2
# Versión: 1.2 (Añadida opción para mover el archivo convertido a la carpeta ISO)

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar cabeceras
show_header() {
    clear
    echo -e "${YELLOW}"
    echo "╔══════════════════════════════════════════╗"
    echo "║   CONVERSOR A QCOW2 PARA VIRT-MANAGER   ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Función para verificar dependencias
check_dependencies() {
    if ! command -v qemu-img &> /dev/null; then
        echo -e "${RED}Error: qemu-img no está instalado.${NC}"
        echo "Instale con: sudo apt install qemu-utils"
        exit 1
    fi
}

# Función para seleccionar ruta base
select_base_path() {
    show_header
    echo "Seleccione la ubicación base:"
    echo "1) ~/Proyecto-ASIR2/machines/ataque"
    echo "2) ~/Proyecto-ASIR2/machines/defensa"
    read -p "Opción [1/2]: " base_option

    case $base_option in
        2) BASE_PATH="$HOME/Proyecto-ASIR2/machines/defensa" ;;
        *) BASE_PATH="$HOME/Proyecto-ASIR2/machines/ataque" ;;
    esac

    if [ ! -d "$BASE_PATH" ]; then
        echo -e "${RED}Error: No se encontró el directorio $BASE_PATH${NC}"
        exit 1
    fi
}

# Función para seleccionar subdirectorio
select_subdirectory() {
    show_header
    echo -e "Directorios disponibles en ${GREEN}$BASE_PATH${NC}:"
    echo "----------------------------------------"

    dir_options=()
    while IFS= read -r dir; do
        dir_options+=("$dir")
    done < <(find "$BASE_PATH" -maxdepth 1 -type d | sort | tail -n +2)

    for i in "${!dir_options[@]}"; do
        echo "$((i+1))) ${dir_options[$i]##*/}"
    done

    read -p "Seleccione el directorio [1-${#dir_options[@]}]: " dir_choice

    SELECTED_DIR="${dir_options[$((dir_choice-1))]}"
    if [ ! -d "$SELECTED_DIR" ]; then
        echo -e "${RED}Error: Directorio no válido${NC}"
        exit 1
    fi
}

# Función para seleccionar archivo
select_file_to_convert() {
    show_header
    echo -e "Archivos disponibles en ${GREEN}$SELECTED_DIR${NC}:"
    echo "----------------------------------------"

    file_options=()
    while IFS= read -r file; do
        file_options+=("$file")
    done < <(find "$SELECTED_DIR" -type f \( -iname "*.vmdk" -o -iname "*.vdi" -o -iname "*.raw" \))

    if [ ${#file_options[@]} -eq 0 ]; then
        echo -e "${RED}No se encontraron archivos compatibles (.vmdk, .vdi, .raw)${NC}"
        exit 1
    fi

    for i in "${!file_options[@]}"; do
        echo "$((i+1))) ${file_options[$i]##*/}"
    done

    read -p "Seleccione el archivo a convertir [1-${#file_options[@]}]: " file_choice

    INPUT_FILE="${file_options[$((file_choice-1))]}"
    OUTPUT_FILE="${INPUT_FILE%.*}.qcow2"
}

# Función para confirmar
confirm_conversion() {
    show_header
    echo -e "${YELLOW}Resumen de la conversión:${NC}"
    echo "----------------------------------------"
    echo -e "Archivo origen:  ${GREEN}$INPUT_FILE${NC}"
    echo -e "Archivo destino: ${GREEN}$OUTPUT_FILE${NC}"
    echo "----------------------------------------"

    read -p "¿Desea continuar con la conversión? [s/N]: " confirm
    if [[ ! "$confirm" =~ ^[sS]$ ]]; then
        echo -e "${RED}Conversión cancelada${NC}"
        exit 0
    fi
}

# Función para convertir
convert_to_qcow2() {
    echo -e "${YELLOW}Iniciando conversión...${NC}"
    
    if [ -f "$OUTPUT_FILE" ]; then
        read -p "El archivo $OUTPUT_FILE ya existe. ¿Sobreescribir? [s/N]: " overwrite
        if [[ ! "$overwrite" =~ ^[sS]$ ]]; then
            echo -e "${RED}Conversión cancelada${NC}"
            exit 0
        fi
        rm -f "$OUTPUT_FILE"
    fi

    if qemu-img convert -O qcow2 "$INPUT_FILE" "$OUTPUT_FILE"; then
        echo -e "${GREEN}✔ Conversión completada con éxito${NC}"
        echo -e "Archivo creado: ${GREEN}$OUTPUT_FILE${NC}"
        chmod 644 "$OUTPUT_FILE"
        echo -e "Permisos ajustados a 644"
    else
        echo -e "${RED}✖ Error durante la conversión${NC}"
        exit 1
    fi
}

# Función para mover a carpeta ISO
ask_destination_path() {
    echo
    read -p "¿Desea mover el archivo convertido a ~/Proyecto-ASIR2/machines/iso? [s/N]: " move_choice
    if [[ "$move_choice" =~ ^[sS]$ ]]; then
        ISO_DIR="$HOME/Proyecto-ASIR2/machines/iso"
        mkdir -p "$ISO_DIR"
        mv "$OUTPUT_FILE" "$ISO_DIR/"
        echo -e "${GREEN}✔ Archivo movido a: $ISO_DIR/${OUTPUT_FILE##*/}${NC}"
    else
        echo -e "${YELLOW}✔ Archivo conservado en su ubicación actual${NC}"
    fi
}

# --- Ejecución principal ---
check_dependencies
select_base_path
select_subdirectory
select_file_to_convert
confirm_conversion
convert_to_qcow2
ask_destination_path

exit 0
