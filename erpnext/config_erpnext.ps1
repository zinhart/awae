Import-Module Posh-SSH;
[string]$userName = 'frappe'
[string]$userPassword = 'frappe'
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force
[pscredential]$credObject = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)

$worker = New-SSHSession -ComputerName erpnext -Credential $credObject
$webServerServicesSession = New-SSHSession -ComputerName erpnext -Credential $credObject
$webServerSession = New-SSHSession -ComputerName erpnext -Credential $credObject
$AWAE_IP = ip a | grep 'inet .* tun0' | awk -F " " '{print $2}' | sed 's/...$//g'


if (-not(Test-Path './site_config.json' -PathType Leaf)) {
    echo '{' >> site_config.json;
    echo '"db_name": "_1bd3e0294da19198",' >> site_config.json;
    echo '"db_password": "32ldabYvxQanK4jj",' >> site_config.json;
    echo '"db_type": "mariadb",' >> site_config.json;
    echo "`"mail_server`": `"$AWAE_IP`"," >> site_config.json;
    echo '"use_ssl": 0,' >> site_config.json;
    echo '"mail_port": 25,' >> site_config.json;
    echo '"auto_email_id": "admin@randomdomain.com"' >> site_config.json;
    echo '}' >> site_config.json;
}

# copy site_config.json to frappe-bench/sites/site1.local/site_config.json
Set-SCPItem -ComputerName erpnext -Credential $credObject -Path './site_config.json' -Destination '/home/frappe/frappe-bench/sites/site1.local/' -Verbose

# Set up Local Email server for debugging emails
Start-Job -ScriptBlock { python3 -m smtpd -n -c DebuggingServer 0.0.0.0:25; }

# install remote debugging server python module
Invoke-SSHCommand -Command '/home/frappe/frappe-bench/env/bin/pip install ptvsd' -SSHSession $worker

# update app.py to enable remote debugging 
Set-SCPItem -ComputerName erpnext -Credential $credObject -Path './app.py' -Destination '/home/frappe/frappe-bench/apps/frappe/frappe' -Verbose

# rsync command here
sshpass -p frappe rsync -azP frappe@erpnext:/home/frappe/frappe-bench .

<#
# start up services for the frappe webserver (should be in a separate ssh connection)
Invoke-SSHCommand -Command 'cd /home/frappe/frappe-bench; bench start' -SSHSession $webServerServicesSession
#>

<#
# startup the webserver itself (should be in a separate ssh connection)
Invoke-SSHCommand -Command 'cd /home/frappe/frappe-bench/sites; ../env/bin/python ../apps/frappe/frappe/utils/bench_helper.py frappe serve --port 8000 --noreload --nothreading' -SSHSession $webServerSession
#>

<#

sshpass -p 'frappe' scp site_config.json frappe@erpnext:/home/frappe/frappe-bench/sites/site1.local/site_config.json;

# install remote debugging server python module
sshpass -p 'frappe' ssh frappe@erpnext -t '/home/frappe/frappe-bench/env/bin/pip install ptvsd';
# enable remote debugging server
sshpass -p 'frappe' scp app.py frappe@erpnext:/home/frappe/frappe-bench/apps/frappe/frappe/app.py;
# rsync command here
sshpass -p frappe rsync -azP frappe@erpnext:/home/frappe/frappe-bench .
# start up services for the frappe webserver (should be in a separate ssh connection)
sshpass -p 'frappe' ssh frappe@erpnext -t 'cd /home/frappe/frappe-bench; bench start';
# startup the webserver itself (should be in a separate ssh connection)
cd /home/frappe/frappe-bench/sites; ../env/bin/python ../apps/frappe/frappe/utils/bench_helper.py frappe serve --port 8000 --noreload --nothreading


#>
Remove-Item site_config.json