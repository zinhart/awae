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
  foreach($word in $word_list) {
    foreach($action in $actions_list) {
      $url = "http://apigateway:8000/files/import" #"$target/$word/$action"
      #write-output $url
      $res_get = Invoke-WebRequest -Uri $url -Method Get -SkipHttpErrorCheck
      $res_post = Invoke-WebRequest -Uri $url -Method Post -SkipHttpErrorCheck
      $res_put = Invoke-WebRequest -Uri $url -Method Put -SkipHttpErrorCheck
      $res_patch = Invoke-WebRequest -Uri $url -Method Patch -SkipHttpErrorCheck
      <#if( ($res_get.StatusCode -notin $ignore_status_codes) -or ($res_post.StatusCode -notin $ignore_status_codes) -or ($res_put.StatusCode -notin $ignore_status_codes -or ($res_patch.StatusCode -notin $ignore_status_codes))#>
if( ($res_get.StatusCode -notin $ignore_status_codes) -or ($res_post.StatusCode -notin $ignore_status_codes)
      ) {
        $props = [ordered]@{
          URI = $url
          GET = $res_get.StatusCode
          POST = $res_post.StatusCode
          PUT = $res_put.StatusCode
          PATCH = $res_patch.StatusCode
        }
        $result = New-Object -TypeName PSObject -Property $props
        write-output $result | FT
        break
      }
    }
    break
  }
  
}
