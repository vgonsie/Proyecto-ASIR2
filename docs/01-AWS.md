# 1.- Creación de una instancia en AWS con Ubuntu Server

La creación de una máquina virtual en AWS utilizando Ubuntu Server es un proceso sencillo y bien estructurado. A continuación, se presentan los pasos necesarios para configurar y lanzar una instancia EC2 en AWS.

## Acceso a AWS y selección de instancia

- Inicio de sesión en AWS: Iniciar sesión en la cuenta de AWS mediante este link: AWS Academy Login

- Lanzar laboratorio: En el panel de control, abrir “AWS Academy Learner Lab” y en “Contenidos” dirigirse a “Lanzamiento del Laboratorio para el alumnado de AWS Academy” y pulsar el “Start Lab” para encenderlo y hacer clic en AWS para abrir la página de inicio de la consola.

## Selección de EC2

- Instalar el servicio EC2 para lanzar instancias que usaremos para el proyecto.

## Lanzar una nueva instancia

- En el panel de EC2, selecciona "Instancias (en ejecución)" y luego haz clic en el botón naranja para lanzar una nueva instancia.

## Configuración de la instancia

- Nombre: Proyecto
- Imagen: Ubuntu 24.04 LTS
- Par de claves: vockey

### Configuraciones de red (activar):

- Permitir el tráfico de HTTPS desde Internet
- Permitir el tráfico de HTTP desde Internet

## IP Elástica

- En el panel lateral izquierdo, apartado de “Red y seguridad”, dirigirnos a “Direcciones IP elásticas” y en el botón naranja, creamos una nueva dirección IP elástica la cual asignaremos a nuestra instancia que acabamos de crear.

## Archivo PEM

- En la página del laboratorio > AWS Details, podremos descargar el archivo PEM, que contendrá nuestra clave cifrada, para poder conectar a la instancia que acabamos de crear mediante SSH con el siguiente comando: 