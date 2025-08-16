# Configuración del servidor
SERVER_IP = "localhost"  # Cambiar por IP pública
MANAGER_PORT = 5000

# Configuración de VMs
RAM_GB = 4               # Memoria por VM
CPU_CORES = 2            # Núcleos CPU por VM
MAX_SESSIONS = 5         # Máximo de sesiones concurrentes

# Versiones de Windows disponibles
WINDOWS_VERSIONS = {
    "win10": "Windows 10",
    "win11": "Windows 11",
    "server2022": "Windows Server 2022"
}

# Tiempo máximo de sesión en minutos (0 = ilimitado)
MAX_SESSION_MINUTES = 120
