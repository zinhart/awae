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
  
  <#
  for($i = 0; $i -lt $Methods.Length; ++$i ) {
    $key = $Methods[$i].toLower()
    if($key -in $map.Keys) {
      write-output 'here'
      $map[$key] = 'apples' 
    }
    #$Methods[$i] = $Methods[$i].toLower()
  }
  foreach($t in $map.Keys){if ($map[$t] -ne $null){ write-output $t}}
  #>
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
        }
      # make requests
      foreach($method in $Methods) {
        $resp = Invoke-WebRequest -Uri $url -Method $method -SkipHttpErrorCheck
        #if( $resp.StatusCode -notin $ignore_status_codes ) {
          $map[$method] = $resp
        #}
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



      <#
      for($k = 0; $k -lt $Methods.Length; ++$k ) {
        $status_code = "$($Methods[$k])"
        $resp_obj = "$($Methods[$k])_RES"
        $props2[$status_code] = $map[$Methods[$k]].StatusCode
        $props2["$resp_obj"] = $map[$Methods[$k]]
      }
      #>
      #$props2
      #$result = New-Object -TypeName PSObject -Property $props2
      #write-output $result
      # build output
      <#
      for($k = 0; $k -lt $Methods.Length; ++$k ) {
        #write-host $key
        $resp = Invoke-WebRequest -Uri $url -Method $Methods[$k] -SkipHttpErrorCheck

        if( $resp.StatusCode -notin $ignore_status_codes ) {
          write-host "$url $($resp.StatusCode) $($Methods[$k])"
          $props2["$($Methods[$k])"] = $resp.StatusCode
        #Write-Output $key $resp.StatusCode
          #$props2["$($key)_RES"] = $res

          #Write-Output $props2
        }
          #$test = New-Object -TypeName PSObject -Property $props2
          #Write-Output $test

      }
      #$test = New-Object -TypeName PSObject -Property $props2
      #Write-Output $test
      #>
      <#
      $res_get = Invoke-WebRequest -Uri $url -Method Get -SkipHttpErrorCheck
      $res_post = Invoke-WebRequest -Uri $url -Method Post -SkipHttpErrorCheck
      if( ($res_get.StatusCode -notin $ignore_status_codes) -or ($res_post.StatusCode -notin $ignore_status_codes)) {
        $props = [ordered]@{
          URI = $url
          GET = $res_get.StatusCode
          POST = $res_post.StatusCode
          GET_RES = $res_get
          POST_RES = $res_post
        }
        $found = New-Object -TypeName PSObject -Property $props
        #Write-Output $found
      }
      #>
    }
  }
}
