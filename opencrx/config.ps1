Import-Module Posh-SSH;
[string]$target = 'opencrx'
[string]$userName = 'student'
[string]$userPassword = 'studentlab'
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force
[pscredential]$credObject = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)
<#
$worker = New-SSHSession -ComputerName $target -Credential $credObject

function Write-Log($result, $message_success, $message_fail) {
    if ( $result.ExitStatus -eq 0 ) {
     
      Write-Host "$message_success $($result.Output)"
    }
    else {
        Write-Host $message_fail
    }
}
$result = Invoke-SSHCommand -Command "cd /home/student/crx/apache-tomee-plus-7.0.5/bin; ./opencrx.sh run" -SSHSession $worker
Write-Log $result 'Success' 'Fail'
#>

$mount_dir='/home/vagrant/Desktop/opencrx-working'
mkdir -p $mount_dir
echo $userPassword | sshfs -o password_stdin -o allow_other "$($userName)@$($target):/home/student/crx/apache-tomee-plus-7.0.5/bin" $mount_dir
