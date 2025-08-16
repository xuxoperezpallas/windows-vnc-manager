param(
    [string]$vmName
)

# Detener y eliminar VM
Stop-VM -Name $vmName -Force -Confirm:$false
Remove-VM -Name $vmName -Force -Confirm:$false

# Eliminar mapeo NAT
Get-NetNatStaticMapping | Where-Object {$_.VMName -eq $vmName} | Remove-NetNatStaticMapping
