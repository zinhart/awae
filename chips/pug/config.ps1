Import-Module Posh-SSH;
[string]$userName = 'student'
[string]$userPassword = 'studentlab'
[string]$machine = 'chips'
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force
[pscredential]$credObject = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)

$worker = New-SSHSession -ComputerName $machine -Credential $credObject
$worker
$result = Invoke-SSHCommand -Command 'docker-compose -f /home/student/chips/docker-compose.yml down && export TEMPLATING_ENGINE=pug && docker-compose -f /home/student/chips/docker-compose.yml up -d' -SSHSession $worker
$result

Write-Output "Allowing application to start up sleeping for 10 seconds ..."
Start-Sleep -Seconds 10

iwr -Uri http://chips | sls -Pattern '<!-- Using Pug as Templating Engine-->' | % -process {$_.Matches.Value}
