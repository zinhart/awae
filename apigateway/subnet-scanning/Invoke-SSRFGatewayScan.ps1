<#
.SYNOPSIS
  This is a simple template script for gateway detection on an internal network via blind SSRF.
.Description
  This script enumerates hosts on the local intranet behind reverse proxies/apigateways.
.PARAMETER Target
  A full uri that we want to scan for.
.PARAMETER SSRF
  The SSRF target that we will scan through.
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
  PS> Invoke-SSRFPortScan -Target http://apigateway:8000/files/import -SSRF http://localhost
#>
function Invoke-SSRFGatewayScan() {
  [cmdletbinding()]
  param(
  [Parameter(Mandatory=$true, HelpMessage='The target URI')]
  [string]$Target,
  [Parameter(Mandatory=$true, HelpMessage='The SSRF target that we will scan through.')]
  [string]$SSRF,
  [Parameter(Mandatory=$false, HelpMessage='Number of seconds before moving onto the next port')]
  [int]$Timeout = 5,
  [Parameter(Mandatory=$false, HelpMessage='Show Only Open ports')]
  [switch]$Live
  )
    
}