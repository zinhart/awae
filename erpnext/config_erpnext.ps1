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

# disable auto debugging
Invoke-SSHCommand -Command "sudo sed -i 's/web: bench serve --port 8000/#web: bench serve --port 8000/g' /home/frappe/frappe-bench/Procfile" -SSHSession $worker

# update app.py to enable remote debugging
Set-SCPItem -ComputerName erpnext -Credential $credObject -Path './app.py' -Destination '/home/frappe/frappe-bench/apps/frappe/frappe' -Verbose

# start up services for the frappe webserver (should be in a separate ssh connection)
Invoke-SSHCommand -Command 'cd /home/frappe/frappe-bench; bench start' -SSHSession $webServerServicesSession

# startup the webserver itself (should be in a separate ssh connection)
Invoke-SSHCommand -Command 'cd /home/frappe/frappe-bench/sites; ../env/bin/python ../apps/frappe/frappe/utils/bench_helper.py frappe serve --port 8000 --noreload --nothreading &' -SSHSession $webServerSession

Remove-Item site_config.json

# fix up mysql logging  
Invoke-SSHCommand -Command "sudo sed -i 's/#general_log/general_log/g' /etc/mysql/my.cnf" -SSHSession $worker
Invoke-SSHCommand -Command "sudo systemctl restart mysql" -SSHSession $worker

# rsync command here
# sshpass -p frappe rsync -azP frappe@erpnext:/home/frappe/frappe-bench .
# remote mouting is MUCH faster
$mount_dir='/home/vagrant/Desktop/erpnext-working'
mkdir -p $mount_dir
sshfs -o allow_other frappe@erpnext:/home/frappe/frappe-bench $mount_dir
mkdir -p $mount_dir/.vscode
$launch_json="$mount_dir/.vscode/launch.json"

echo '{' >> $launch_json
echo '    "version": "0.2.0",' >> $launch_json
echo '    "configurations": [' >> $launch_json
echo '       {' >> $launch_json
echo '           "name": "Python: Remote Attach",' >> $launch_json
echo '           "type": "python",' >> $launch_json
echo '           "request": "attach",' >> $launch_json
echo '           "connect": {' >> $launch_json
echo '               "host": "erpnext",' >> $launch_json
echo '               "port": 5678' >> $launch_json
echo '           },' >> $launch_json
echo '           "pathMappings": [' >> $launch_json
echo '               {' >> $launch_json
echo "                   `"localRoot`": `"$mount_dir`"," >> $launch_json
echo '                   "remoteRoot": "/home/frappe/frappe-bench/"' >> $launch_json
echo '               }' >> $launch_json
echo '           ],' >> $launch_json
echo '           "justMyCode": true' >> $launch_json
echo '       }' >> $launch_json
echo '   ]' >> $launch_json
echo '}' >> $launch_json