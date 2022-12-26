<#
.Description
This is a commandlet used to enumerate microservices via http verb tampering
.PARAMETER ActionList
The string that you want to hash.
.PARAMETER Target
The hashing algorithm.
.PARAMETER Wordlist
.EXAMPLE
PS> Invoke-RouteBuster -ActionList /usr/share/wordlists/dirb/small.txt -Wordlist endpoints-stripped.txt -Target http://apigateway:8000
.SYNOPSIS
Providing a more unified experience to computing string hashes when using pwsh on Linux.
#>
function Invoke-RouteBuster() {
  param(
  [Parameter(Mandatory=$true, HelpMessage='Specify string to be hashed. Accepts from pipeline.')]
  [string]$ActionList,
  [Parameter(Mandatory=$true, HelpMessage='abc')]
  [string]$Target,
  [Parameter(Mandatory=$true, HelpMessage='abc')]
  [string]$Wordlist,
  [Parameter(Mandatory = $false, HelpMessage = 'abc')]
  [String[]] $Methods = @('GET', 'POST'),
  [Parameter(Mandatory = $false, HelpMessage = 'Filter displayed status codes')]
  [Int32[]] $DisplayFilter
  )
  $actions_list = Get-Content $ActionList
  $word_list = Get-Content $Wordlist
  $ignore_status_codes = 204,401,403,404
 
  for($i = 0; $i -lt $word_list.Length; ++$i ) {
    $outer_percent_complete = [System.Math]::Round($i / $word_list.Length * 100)
    Write-Progress -Id 1 -Activity "Current Word: $($word_list[$i])" -Status "$outer_percent_complete% Complete:" -PercentComplete $outer_percent_complete;
    for($j = 0; $j -lt $actions_list.Length; ++$j ) {
      $url = "$($target)/$($word_list[$i])/$($actions_list[$j])"
      $inner_percent_complete = [System.Math]::Round($j / $actions_list.Length * 100,2)
      Write-Progress -ParentId 1 -Activity "Url: $url" -Status "$inner_percent_complete% Complete:" -PercentComplete $inner_percent_complete;
      $map = [ordered]@{
          'GET'   = $null
          'POST'  = $null
          'PUT'   = $null
          'PATCH' = $null
          'DELETE' = $null
        }
      # make requests
      foreach($method in $Methods) {
        $resp = Invoke-WebRequest -Uri $url -Method $method -SkipHttpErrorCheck
          $map[$method] = $resp
      }
      # ignore all of the null values in map, which effectively are methods not chosen
      $filtered_responses = $map.GetEnumerator() | ? { $null  -ne $_.Value}
      
      $include = $false
      foreach($iter in $filtered_responses.GetEnumerator()) {
        if( $iter.Value.StatusCode -notin $ignore_status_codes) {
          $include = $true
          break;
        }
      }
      if($include) {
        $props2 = [ordered]@{
          URI = $url
        }
        foreach($resp in $filtered_responses.GetEnumerator()) {
          $status_code = "$($resp.Key.toUpper())"
          $props2[$status_code] = $resp.Value.StatusCode
        }
        # We do this separately to enforce ordering
        foreach($resp in $filtered_responses.GetEnumerator()) {
          $resp_obj = "$($resp.Key.toUpper())_RES"
          $props2["$resp_obj"] = $resp.Value
        }
        # even though certain requests maybe not be valid it's still interesting to see how the reponses that were not filtered out in comparison
        if($include) {
        $result = New-Object -TypeName PSObject -Property $props2
        write-output $result
        }
      }
    }
  }
}
