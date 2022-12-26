<#
.SYNOPSIS
URLs for RESTful APIs often follow a pattern of <object>/<action> or <object>/<identifier>. We might be able to discover more services by taking the list of endpoints we have already identified and iterating through a wordlist to find valid actions or identifiers. We also need to keep in mind that web APIs might respond differently based on which HTTP request method we use.
For example, a GET request to /auth might return an HTTP 404 response, while a POST request to the same URL returns an HTTP 200 OK on a valid login or an HTTP 401 Unauthorized on an invalid login attempt.
This script returns the URI, HTTP Status Code per method, and the Response object to STDOUT.
Therefore you easily do something like:
$test = Invoke-RouteBuster -ActionList ./actions-only-valid.txt -Wordlist ./wordlist-only-valid.txt -Target http://apigateway:8000 -Methods get,post
$test[0]
.Description
The purpose of this script is to enumerate microservices built with Restful API's via HTTP verb tampering
.PARAMETER ActionList
The actions list. For Instance take /password/reset. reset would be the action
.PARAMETER Wordlist
The actions list. For Instance take /password/reset. password would be from our wordlist
.PARAMETER Target
The full target URI
.PARAMETER Methods
A list of HTTP methods to use, i.e get,post,put,patch,delete
.PARAMETER DisplayFilter
A list to filter responses based on HTTP status codes.
.EXAMPLE
PS> Invoke-RouteBuster -ActionList /usr/share/wordlists/dirb/small.txt -Wordlist endpoints-stripped.txt -Target http://apigateway:8000
.NOTES
  Version:        1.0
  Author:         Zinhart
  Purpose/Change: Created while studying for OSWE certification
#>
function Invoke-RouteBuster() {
  param(
  [Parameter(Mandatory=$true, HelpMessage='A list of actions to try against known endpoints.')]
  [string]$ActionList,
  [Parameter(Mandatory=$true, HelpMessage='Target URI.')]
  [string]$Target,
  [Parameter(Mandatory=$true, HelpMessage='A list of preferrable known endpoints.')]
  [string]$Wordlist,
  [Parameter(Mandatory = $false, HelpMessage = 'HTTP Methods to Use With Verb Tampering.')]
  [String[]] $Methods = @('GET', 'POST'),
  [Parameter(Mandatory = $false, HelpMessage = 'Filter displayed status codes.')]
  [Int32[]] $DisplayFilter = @(204,401,403,404)
  )
  $actions_list = Get-Content $ActionList
  $word_list = Get-Content $Wordlist
 
  for($i = 0; $i -lt $word_list.Length; ++$i ) {
    $outer_percent_complete = [System.Math]::Round($i / $word_list.Length * 100)
    Write-Progress -Id 1 -Activity "Current Word: $($word_list[$i])" -Status "$outer_percent_complete% Complete:" -PercentComplete $outer_percent_complete;
    for($j = 0; $j -lt $actions_list.Length; ++$j ) {
      $url = "$($target)/$($word_list[$i])/$($actions_list[$j])"
      $inner_percent_complete = [System.Math]::Round($j / $actions_list.Length * 100,2)
      Write-Progress -ParentId 1 -Activity "Url: $url" -Status "$inner_percent_complete% Complete:" -PercentComplete $inner_percent_complete;
      $map = [ordered]@{
          'GET'    = $null
          'POST'   = $null
          'PUT'    = $null
          'PATCH'  = $null
          'DELETE' = $null
      }
      # make requests
      foreach($method in $Methods) {
        $resp = Invoke-WebRequest -Uri $url -Method $method -SkipHttpErrorCheck
          $map[$method] = $resp
      }
      # ignore all of the null values in map, which effectively are methods not chosen
      $filtered_responses = $map.GetEnumerator() | ? { $null  -ne $_.Value }
      
      # when there is only one verb force $filtered_responses to be an array
      if($filtered_responses -isnot [array]){
        $filtered_responses = @($filtered_responses)
      }
      

      # even though certain requests maybe not be valid it's still interesting to see how the reponses that were not filtered out in comparison     
      $include = $false
      foreach($iter in $filtered_responses.GetEnumerator()) {
        if( $iter.Value.StatusCode -notin $DisplayFilter) {
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

        if($include) {
        $result = New-Object -TypeName PSObject -Property $props2
        write-output $result
        }
      }
    }
  }
}
