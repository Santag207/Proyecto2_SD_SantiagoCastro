
## Simulador Distribuido de Transporte

Este proyecto es una simulación de un sistema de transporte similar a Uber, desarrollado como parte del curso de **Sistemas Distribuidos**. Su diseño incluye **comunicación entre procesos**, **tolerancia a fallos**, y un sistema de monitoreo para garantizar la operación continua del servicio. La implementación utiliza **ZeroMQ** para manejar la mensajería entre componentes.

---

### **Características Principales**

1. **Escenario de Simulación**:
   - La ciudad está modelada como una cuadrícula donde los taxis se mueven y responden a solicitudes de usuarios.
   - Los usuarios envían peticiones para solicitar un taxi desde ubicaciones específicas.
   
2. **Arquitectura Distribuida**:
   - **Servidor Principal**: Coordina la comunicación entre los usuarios y los taxis, asignando servicios según la disponibilidad.
   - **Servidor de Respaldo**: Asume el control automáticamente en caso de una falla en el Servidor Principal.
   - **Monitoreo de Salud**: Evalúa constantemente el estado del sistema y activa el servidor de respaldo si detecta un fallo.

3. **Componentes del Sistema**:
   - **Usuarios**: Enviados como hilos, generan solicitudes de servicios y esperan una respuesta.
   - **Taxis**: Procesos individuales que reportan su ubicación y disponibilidad.
   - **HealthCheck**: Supervisión activa del Servidor Principal para garantizar la continuidad del servicio.

---

### **Tecnologías Clave**

- **ZeroMQ**: Middleware ligero para la comunicación eficiente entre procesos distribuidos.
- **Python**: Lenguaje de programación utilizado para el desarrollo de todos los componentes.
- **JSON**: Formato de almacenamiento de datos persistentes para registrar las estadísticas y servicios del sistema.

---

### **Estructura del Proyecto**

El proyecto incluye los siguientes archivos y módulos:

- **`servidorcentral.py`**: Implementación del Servidor Principal, que coordina las solicitudes y asignaciones de taxis.
- **`servidorreplica.py`**: Código para el Servidor de Respaldo, que entra en operación ante fallos del Servidor Principal.
- **`usuarios.py`**: Simulación de usuarios que generan solicitudes de taxis.
- **`taxi1.py`, `taxi2.py`**: Representan taxis individuales como procesos independientes que interactúan con los servidores.
- **`healthcheck.py`**: Componente encargado de monitorear la disponibilidad del Servidor Principal.
- **`config.py`**: Archivo de configuración para establecer las direcciones IP y puertos utilizados por los componentes.
- **`datos_taxis.json`**: Archivo JSON que almacena la información de los taxis, los servicios realizados, y las estadísticas del sistema.
- **`README.md`**: Documento que describe el proyecto y su implementación.

---

### **Cómo Funciona**

1. **Configuración Inicial**:
   - Los servidores y los taxis son configurados con puertos e IPs definidos en `config.py`.
   - Los datos iniciales de los taxis están almacenados en `datos_taxis.json`.

2. **Inicio del Sistema**:
   - El Broker inicia como intermediario de comunicación entre todos los componentes.
   - Los taxis comienzan a enviar su posición actual y estado al Servidor Principal.

3. **Procesamiento de Solicitudes**:
   - Los usuarios envían solicitudes de servicios indicando su posición.
   - El Servidor Principal asigna un taxi disponible según la proximidad.

4. **Resiliencia**:
   - El proceso de monitoreo activa el Servidor de Respaldo si detecta un fallo en el Servidor Principal.

---

### **Créditos**

Este proyecto fue desarrollado con fines educativos, aplicando conceptos de sistemas distribuidos, manejo de procesos, y tolerancia a fallos. Su implementación es modular para facilitar la comprensión y extensión del sistema.

---

### **Ejecutar el Proyecto**

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Iniciar el broker:
   ```bash
   python broker.py
   ```

3. Ejecutar el Servidor Principal:
   ```bash
   python servidorcentral.py
   ```

4. Ejecutar el Servidor de Respaldo:
   ```bash
   python servidorreplica.py --replica
   ```

5. Lanzar usuarios y taxis:
   ```bash
   python usuarios.py
   python taxi1.py
   python taxi2.py
   ```
