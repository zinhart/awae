<#
.SYNOPSIS
  Given a CIDR (Classless Inter-Domain Routing) format network address, generate all valid IPv4 addresses in that range.
.DESCRIPTION
  Given a CIDR (Classless Inter-Domain Routing) format network address, generate all valid IPv4 addresses in that range.
.PARAMETER NetworkAddress
  The network address written in CIDR format 'a.b.c.d/#' and an example would be '192.168.1.24/27'. Can be a single value, an
  array of values, or values can be taken from the pipeline.
.PARAMETER Enumerate
  Enumerates all IPs in subnet (potentially resource-expensive). Ignored if you use -Contains.
.PARAMETER Gateway
  Enumerates all Potential Gateways for each possible subnet (potentially resource-expensive). Ignored if you use -Contains.
.PARAMETER Contains
  Return a boolean value for whether the specified IP is in the specified network. Includes network address and broadcast address.
.EXAMPLE
  '172.16.0.0/24' | ./Convert-CIDRInfo.ps1
.EXAMPLE
  ./Convert-CIDRInfo.ps1 -NetworkAddress '172.16.0.0/12' -Gateway
.EXAMPLE
  ./Convert-CIDRInfo.ps1 -NetworkAddress '172.16.0.0/12' -Enumerate
.NOTES
  Version:        1.0
  Author:         Zinhart
  Purpose/Change: Created while studying for OSWE certification
  Inspired by: https://github.com/EliteLoser/PSipcalc/blob/master/PSipcalc.ps1 
#>
#requires -version 2
[CmdletBinding()]
param(
    [Parameter(Mandatory=$True, ValueFromPipeline = $True, HelpMessage="The network address written in CIDR format 'a.b.c.d/#' and an example would be '192.168.1.24/27'. Can be a single value, an
  array of values, or values can be taken from the pipeline.")]
    [string[]] $NetworkAddress,
    [Parameter(Mandatory=$False,HelpMessage="Enumerates all IPs in subnet (potentially resource-expensive). Ignored if you use -Contains.")]
    [switch] $Enumerate,
    [Parameter(Mandatory=$False,HelpMessage="Enumerates all Potential Gateways for each possible subnet (potentially resource-expensive). Ignored if you use -Contains.")]
    [switch] $Gateway,
    [Parameter(Mandatory=$False,HelpMessage="Return a boolean value for whether the specified IP is in the specified network. Includes network address and broadcast address.")]
    [string] $Contains
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
# this regex is a bit cleaner than the original for detecting ipv4 addresses.
$IPv4Regex = '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

function Convert-IPToBinary
{
    param(
        [string] $IP
    )
    $IP = $IP.Trim()
    if ($IP -match "\A${IPv4Regex}\z")
    {
        try
        {
            return ($IP.Split('.') | ForEach-Object { [System.Convert]::ToString([byte] $_, 2).PadLeft(8, '0') }) -join ''
        }
        catch
        {
            Write-Warning -Message "Error converting '$IP' to a binary string: $_"
            return $Null
        }
    }
    else
    {
        Write-Warning -Message "Invalid IP detected: '$IP'."
        return $Null
    }
}

function Convert-BinaryToIP
{
    param(
        [string] $Binary
    )
    $Binary = $Binary -replace '\s+'
    if ($Binary.Length % 8)
    {
        Write-Warning -Message "Binary string '$Binary' is not evenly divisible by 8."
        return $Null
    }
    [int] $NumberOfBytes = $Binary.Length / 8
    $Bytes = @(foreach ($i in 0..($NumberOfBytes-1))
    {
        try
        {
            #$Bytes += # skipping this and collecting "outside" seems to make it like 10 % faster
            [System.Convert]::ToByte($Binary.Substring(($i * 8), 8), 2)
        }
        catch
        {
            Write-Warning -Message "Error converting '$Binary' to bytes. `$i was $i."
            return $Null
        }
    })
    return $Bytes -join '.'
}

function Get-ProperCIDR
{
    param(
        [string] $CIDRString
    )
    $CIDRString = $CIDRString.Trim()
    $o = '' | Select-Object -Property IP, NetworkLength
    if ($CIDRString -match "\A(?<IP>${IPv4Regex})\s*/\s*(?<NetworkLength>\d{1,2})\z")
    {
        # Could have validated the CIDR in the regex, but this is more informative.
        if ([int] $Matches['NetworkLength'] -lt 0 -or [int] $Matches['NetworkLength'] -gt 32)
        {
            Write-Warning "Network length out of range (0-32) in CIDR string: '$CIDRString'."
            return
        }
        $o.IP = $Matches['IP']
        $o.NetworkLength = $Matches['NetworkLength']
    }
    elseif ($CIDRString -match "\A(?<IP>${IPv4Regex})[\s/]+(?<SubnetMask>${IPv4Regex})\z")
    {
        $o.IP = $Matches['IP']
        $SubnetMask = $Matches['SubnetMask']
        if (-not ($BinarySubnetMask = Convert-IPToBinary $SubnetMask))
        {
            return # warning displayed by Convert-IPToBinary, nothing here
        }
        # Some validation of the binary form of the subnet mask, 
        # to check that there aren't ones after a zero has occurred (invalid subnet mask).
        # Strip all leading ones, which means you either eat 32 1s and go to the end (255.255.255.255),
        # or you hit a 0, and if there's a 1 after that, we've got a broken subnet mask, amirite.
        if ((($BinarySubnetMask) -replace '\A1+') -match '1')
        {
            Write-Warning -Message "Invalid subnet mask in CIDR string '$CIDRString'. Subnet mask: '$SubnetMask'."
            return
        }
        $o.NetworkLength = [regex]::Matches($BinarySubnetMask, '1').Count
    }
    else
    {
        Write-Warning -Message "Invalid CIDR string: '${CIDRString}'. Valid examples: '192.168.1.0/24', '10.0.0.0/255.0.0.0'."
        return
    }
    # Check if the IP is all ones or all zeroes (not allowed: http://www.cisco.com/c/en/us/support/docs/ip/routing-information-protocol-rip/13788-3.html )
    if ($o.IP -match '\A(?:(?:1\.){3}1|(?:0\.){3}0)\z')
    {
        Write-Warning "Invalid IP detected in CIDR string '${CIDRString}': '$($o.IP)'. An IP can not be all ones or all zeroes."
        return
    }
    return $o
}

function Get-IPRangeNaive
{
    param(
        [string] $StartBinary,
        [string] $EndBinary
    )
    $StartIPArray = @((Convert-BinaryToIP $StartBinary) -split '\.')
    $EndIPArray = ((Convert-BinaryToIP $EndBinary) -split '\.')
    Write-Verbose -Message "Start IP: $($StartIPArray -join '.')"
    Write-Verbose -Message "End IP: $($EndIPArray -join '.')"
    $FirstOctetArray = @($StartIPArray[0]..$EndIPArray[0])
    $SecondOctetArray = @($StartIPArray[1]..$EndIPArray[1])
    $ThirdOctetArray = @($StartIPArray[2]..$EndIPArray[2])
    $FourthOctetArray = @($StartIPArray[3]..$EndIPArray[3])
    # Four levels of nesting... Slow.
    $IPs = @(foreach ($First in $FirstOctetArray)
    {
        foreach ($Second in $SecondOctetArray)
        {
            foreach ($Third in $ThirdOctetArray)
            {
                foreach ($Fourth in $FourthOctetArray)
                {
                    "$First.$Second.$Third.$Fourth"
                }
            }
        }
    })
    $IPs = $IPs | Sort-Object -Unique -Property @{Expression={($_ -split '\.' | ForEach-Object { '{0:D3}' -f [int]$_ }) -join '.' }}
    return $IPs
}

function Get-IPRange
{
    param(
        [string] $StartBinary,
        [string] $EndBinary
    )
    [int64] $StartInt = [System.Convert]::ToInt64($StartBinary, 2)
    [int64] $EndInt = [System.Convert]::ToInt64($EndBinary, 2)
    for ($BinaryIP = $StartInt; $BinaryIP -le $EndInt; $BinaryIP++)
    {
        Convert-BinaryToIP ([System.Convert]::ToString($BinaryIP, 2).PadLeft(32, '0'))
    }
}

function Get-GatewaysEnumerated
{
    param(
        [string] $StartBinary,
        [string] $EndBinary
    )
    [int64] $StartInt = [System.Convert]::ToInt64($StartBinary, 2) + 1 # the gateway is typically at .1
    [int64] $EndInt = [System.Convert]::ToInt64($EndBinary, 2)
    for ($BinaryIP = $StartInt; $BinaryIP -le $EndInt; $BinaryIP+=256)
    {
        Convert-BinaryToIP ([System.Convert]::ToString($BinaryIP, 2).PadLeft(32, '0'))
    }
}

function Test-IPIsInNetwork {
    param(
        [string] $IP,
        [string] $StartBinary,
        [string] $EndBinary
    )
    $TestIPBinary = Convert-IPToBinary $IP
    [int64] $TestIPInt64 = [System.Convert]::ToInt64($TestIPBinary, 2)
    [int64] $StartInt64 = [System.Convert]::ToInt64($StartBinary, 2)
    [int64] $EndInt64 = [System.Convert]::ToInt64($EndBinary, 2)
    if ($TestIPInt64 -ge $StartInt64 -and $TestIPInt64 -le $EndInt64)
    {
        return $True
    }
    else
    {
        return $False
    }
}

function Get-NetworkInformationFromProperCIDR
{
    param(
        [psobject] $CIDRObject
    )
    $o = '' | Select-Object -Property IP, NetworkLength, SubnetMask, NetworkAddress, HostMin, HostMax, 
        Broadcast, UsableHosts, TotalHosts, GatewaysEnumerated, IPEnumerated, BinaryIP, BinarySubnetMask, BinaryNetworkAddress,
        BinaryBroadcast
    $o.IP = [string] $CIDRObject.IP
    $o.BinaryIP = Convert-IPToBinary $o.IP
    $o.NetworkLength = [int32] $CIDRObject.NetworkLength
    $o.SubnetMask = Convert-BinaryToIP ('1' * $o.NetworkLength).PadRight(32, '0')
    $o.BinarySubnetMask = ('1' * $o.NetworkLength).PadRight(32, '0')
    $o.BinaryNetworkAddress = $o.BinaryIP.SubString(0, $o.NetworkLength).PadRight(32, '0')
    if ($Contains)
    {
        if ($Contains -match "\A${IPv4Regex}\z")
        {
            # Passing in IP to test, start binary and end binary.
            return Test-IPIsInNetwork $Contains $o.BinaryNetworkAddress $o.BinaryNetworkAddress.SubString(0, $o.NetworkLength).PadRight(32, '1')
        }
        else
        {
            Write-Error "Invalid IPv4 address specified with -Contains"
            return
        }
    }
    $o.NetworkAddress = Convert-BinaryToIP $o.BinaryNetworkAddress
    if ($o.NetworkLength -eq 32 -or $o.NetworkLength -eq 31)
    {
        $o.HostMin = $o.IP
    }
    else
    {
        $o.HostMin = Convert-BinaryToIP ([System.Convert]::ToString(([System.Convert]::ToInt64($o.BinaryNetworkAddress, 2) + 1), 2)).PadLeft(32, '0')
    }
    [string] $BinaryBroadcastIP = $o.BinaryNetworkAddress.SubString(0, $o.NetworkLength).PadRight(32, '1') # this gives broadcast... need minus one.
    $o.BinaryBroadcast = $BinaryBroadcastIP
    [int64] $DecimalHostMax = [System.Convert]::ToInt64($BinaryBroadcastIP, 2) - 1
    [string] $BinaryHostMax = [System.Convert]::ToString($DecimalHostMax, 2).PadLeft(32, '0')
    $o.HostMax = Convert-BinaryToIP $BinaryHostMax
    $o.TotalHosts = [int64][System.Convert]::ToString(([System.Convert]::ToInt64($BinaryBroadcastIP, 2) - [System.Convert]::ToInt64($o.BinaryNetworkAddress, 2) + 1))
    $o.UsableHosts = $o.TotalHosts - 2
    # ugh, exceptions for network lengths from 30..32
    if ($o.NetworkLength -eq 32)
    {
        $o.Broadcast = $Null
        $o.UsableHosts = [int64] 1
        $o.TotalHosts = [int64] 1
        $o.HostMax = $o.IP
    }
    elseif ($o.NetworkLength -eq 31)
    {
        $o.Broadcast = $Null
        $o.UsableHosts = [int64] 2
        $o.TotalHosts = [int64] 2
        # Override the earlier set value for this (bloody exceptions).
        [int64] $DecimalHostMax2 = [System.Convert]::ToInt64($BinaryBroadcastIP, 2) # not minus one here like for the others
        [string] $BinaryHostMax2 = [System.Convert]::ToString($DecimalHostMax2, 2).PadLeft(32, '0')
        $o.HostMax = Convert-BinaryToIP $BinaryHostMax2
    }
    elseif ($o.NetworkLength -eq 30)
    {
        $o.UsableHosts = [int64] 2
        $o.TotalHosts = [int64] 4
        $o.Broadcast = Convert-BinaryToIP $BinaryBroadcastIP
    }
    else
    {
        $o.Broadcast = Convert-BinaryToIP $BinaryBroadcastIP
    }
    if ($Enumerate)
    {
        $IPRange = @(Get-IPRange $o.BinaryNetworkAddress $o.BinaryNetworkAddress.SubString(0, $o.NetworkLength).PadRight(32, '1'))
        if ((31, 32) -notcontains $o.NetworkLength )
        {
            $IPRange = $IPRange[1..($IPRange.Count-1)] # remove first element
            $IPRange = $IPRange[0..($IPRange.Count-2)] # remove last element
        }
        $o.IPEnumerated = $IPRange
    }
    else {
        $o.IPEnumerated = @()
    }
    if($Gateway)
    {
      $GatewaysEnumerated = @(Get-GatewaysEnumerated $o.BinaryNetworkAddress $o.BinaryNetworkAddress.SubString(0, $o.NetworkLength).PadRight(32, '1'))
      $o.GatewaysEnumerated = $GatewaysEnumerated
    }
    else
    {
        $o.GatewaysEnumerated = @()
    }
    return $o
}

$NetworkAddress | ForEach-Object { Get-ProperCIDR $_ } | ForEach-Object { Get-NetworkInformationFromProperCIDR $_ }