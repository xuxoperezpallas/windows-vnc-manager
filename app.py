import subprocess
import threading
from flask import Flask, render_template, request, redirect, jsonify
import config
import os
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Almacenar información de sesiones activas
active_sessions = {}

def start_windows_session(username, password, version="win10"):
    """Inicia una nueva sesión Windows en Hyper-V"""
    try:
        # Generar nombre único para la VM
        vm_name = f"win-vnc-{username}-{int(time.time())}"
        
        # Ejecutar script PowerShell para crear VM
        script_path = os.path.join(os.getcwd(), "scripts", "create-vm.ps1")
        result = subprocess.run([
            "powershell.exe", 
            "-ExecutionPolicy", "Bypass", 
            "-File", script_path,
            "-vmName", vm_name,
            "-osVersion", version,
            "-vncPassword", password,
            "-ramGB", str(config.RAM_GB),
            "-cpuCores", str(config.CPU_CORES)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"Error al crear VM: {result.stderr}")
            return None
        
        # Extraer puerto VNC del output
        port = None
        for line in result.stdout.split('\n'):
            if "VNC_PORT:" in line:
                port = line.split(":")[1].strip()
                break
        
        if not port:
            raise ValueError("No se pudo determinar el puerto VNC")
        
        # Guardar información de sesión
        session_info = {
            "vm_name": vm_name,
            "username": username,
            "port": port,
            "status": "running",
            "created_at": time.time(),
            "url": f"http://{config.SERVER_IP}:{port}"
        }
        
        active_sessions[vm_name] = session_info
        return session_info
        
    except Exception as e:
        logging.error(f"Error en start_windows_session: {str(e)}")
        return None

@app.route('/')
def index():
    """Página principal con formulario para crear sesiones"""
    return render_template('index.html', windows_versions=config.WINDOWS_VERSIONS)

@app.route('/start-session', methods=['POST'])
def start_session():
    """Inicia una nueva sesión Windows"""
    username = request.form.get('username', 'guest')
    password = request.form.get('password', 'Passw0rd!')
    version = request.form.get('version', 'win10')
    
    session = start_windows_session(username, password, version)
    
    if session:
        return render_template('index.html', 
                              session_url=session['url'],
                              username=username,
                              success=f"Sesión Windows {version} creada con éxito!")
    else:
        return render_template('index.html', 
                              error="Error al crear la sesión. Verifica logs.")

@app.route('/stop-session/<vm_name>')
def stop_session(vm_name):
    """Detiene una sesión Windows"""
    if vm_name in active_sessions:
        try:
            script_path = os.path.join(os.getcwd(), "scripts", "remove-vm.ps1")
            result = subprocess.run([
                "powershell.exe", 
                "-ExecutionPolicy", "Bypass", 
                "-File", script_path,
                "-vmName", vm_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                active_sessions.pop(vm_name)
                return jsonify({"status": "success", "message": f"VM {vm_name} detenida"})
        
        except Exception as e:
            logging.error(f"Error deteniendo VM: {str(e)}")
    
    return jsonify({"status": "error", "message": "VM no encontrada"})

@app.route('/list-sessions')
def list_sessions():
    """Lista las sesiones activas"""
    return jsonify(list(active_sessions.values()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.MANAGER_PORT)
