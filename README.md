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
