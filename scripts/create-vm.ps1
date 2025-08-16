param(
    [string]$vmName,
    [string]$osVersion = "win10",
    [string]$vncPassword = "Passw0rd!",
    [int]$ramGB = 4,
    [int]$cpuCores = 2
)

# Configuración según versión de Windows
$osConfig = @{
    "win10" = @{
        "ImagePath" = "C:\VMs\BaseImages\Win10.vhdx"
        "SwitchName" = "Default Switch"
    }
    "win11" = @{
        "ImagePath" = "C:\VMs\BaseImages\Win11.vhdx"
        "SwitchName" = "Default Switch"
    }
    "server2022" = @{
        "ImagePath" = "C:\VMs\BaseImages\Server2022.vhdx"
        "SwitchName" = "Default Switch"
    }
}

# Verificar si existe la configuración
if (-not $osConfig.ContainsKey($osVersion)) {
    Write-Error "Versión de Windows no soportada: $osVersion"
    exit 1
}

$config = $osConfig[$osVersion]

# Crear nueva VM
New-VM -Name $vmName -MemoryStartupBytes ($ramGB * 1GB) -Generation 2 `
       -VHDPath $config.ImagePath -SwitchName $config.SwitchName

# Configurar procesador
Set-VMProcessor -VMName $vmName -Count $cpuCores

# Configurar red
Set-VMNetworkAdapter -VMName $vmName -DynamicMacAddress

# Asignar puerto VNC (buscar puerto libre)
$vncPort = Get-NetTCPConnection | 
    Where-Object {$_.LocalPort -ge 5900 -and $_.LocalPort -le 6000 -and $_.State -ne "Listen"} | 
    Select-Object -First 1 -ExpandProperty LocalPort

if (-not $vncPort) {
    $vncPort = 5900
}

# Configurar NAT
Add-NatStaticMapping -VMName $vmName -ExternalPort $vncPort -InternalPort 5900 -Protocol TCP

# Iniciar VM
Start-VM -Name $vmName

# Esperar a que la VM arranque
Start-Sleep -Seconds 60

# Configurar VNC (usando comunicación con VM)
# NOTA: Requiere tener configurada comunicación WinRM con la VM
$scriptBlock = {
    param($pass)
    # Instalar y configurar TightVNC
    $vncInstaller = "https://www.tightvnc.com/download/2.8.59/tightvnc-2.8.59-gpl-setup-64bit.msi"
    $installPath = "$env:TEMP\tightvnc.msi"
    Invoke-WebRequest -Uri $vncInstaller -OutFile $installPath
    Start-Process msiexec.exe -ArgumentList "/i $installPath /quiet /norepass" -Wait
    Remove-Item $installPath
    
    # Configurar contraseña
    & "C:\Program Files\TightVNC\tvnserver.exe" -controlservice -password $pass
}

Invoke-Command -VMName $vmName -ScriptBlock $scriptBlock -ArgumentList $vncPassword

# Devolver información de la sesión
Write-Output "VNC_PORT:$vncPort"
Write-Output "VM_NAME:$vmName"
