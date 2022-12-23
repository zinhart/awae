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
  [string]$Wordlist
  )
  $actions_list = Get-Content $ActionList
  $word_list = Get-Content $Wordlist
  $ignore_status_codes = 204,401,403,404
  $results = New-Object -TypeName "System.Collections.ArrayList"
  for($i = 0; $i -lt $word_list.Length; ++$i ) {
    $outer_percent_complete = [System.Math]::Round($i / $word_list.Length * 100)
    Write-Progress -Id 1 -Activity "Current word: $($word_list[$i])" -Status "$outer_percent_complete% Complete:" -PercentComplete $outer_percent_complete;
    for($j = 0; $j -lt $actions_list.Length; ++$j ) {
      $inner_percent_complete = [System.Math]::Round($j / $actions_list.Length * 100,2)
      Write-Progress -ParentId 1 -Activity "Current url: $($actions_list[$j])" -Status "$inner_percent_complete% Complete:" -PercentComplete $inner_percent_complete;
      $url = "http://apigateway:8000/files/import" #"$target/$word_list[$i]/$action_list[$j]"
      #write-output $url
      $res_get = Invoke-WebRequest -Uri $url -Method Get -SkipHttpErrorCheck
      $res_post = Invoke-WebRequest -Uri $url -Method Post -SkipHttpErrorCheck
      if( ($res_get.StatusCode -notin $ignore_status_codes) -or ($res_post.StatusCode -notin $ignore_status_codes)) {
        $props = [ordered]@{
          URI = $url
          GET = $res_get.StatusCode
          POST = $res_post.StatusCode
        }
        $result = New-Object -TypeName PSObject -Property $props
        [void]$results.Add($result)
      }
    }
  }
  Write-Output $results | Format-Table -AutoSize
  
}
