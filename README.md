# Gestor de Sesiones Windows con VNC

Este proyecto permite crear sesiones Windows bajo demanda con acceso VNC, utilizando Hyper-V y PowerShell.

## Características principales

- 🚀 Creación automática de máquinas virtuales Windows
- 🌐 Interfaz web para gestionar sesiones
- 🔒 Configuración segura con contraseñas
- 📊 Visualización de sesiones activas
- ⏱️ Auto-destrucción de sesiones inactivas

## Requisitos previos

- Windows 10/11 Pro o Enterprise
- Hyper-V habilitado
- PowerShell 5.1+
- Python 3.9+

## Instalación

1. **Habilitar Hyper-V**:
   ```powershell
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   Restart-Computer
