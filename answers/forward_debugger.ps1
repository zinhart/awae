# keep getting connecting reset 
<#
Import-Module Posh-SSH;
[string]$userName = 'student'
[string]$userPassword = 'studentlab'
[string]$machine = 'debugger'
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force
[pscredential]$credObject = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)

$worker = New-SSHSession -ComputerName $machine -Credential $credObject
$worker.SessionID
New-SSHLocalPortForward -SSHSession $worker -BoundHost localhost -BoundPort 7080 -RemoteAddress $machine -RemotePort 80 -Verbose 
#>
#$result = New-SSHLocalPortForward -BoundHost localhost -BoundPort 4080 -RemoteAddress $machine -RemotePort 80 -SSHSession $worker
#$result
sshpass -p studentlab ssh -N -L 4080:localhost:80 'student@debugger'