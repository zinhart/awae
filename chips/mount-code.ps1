mkdir -p chips
echo studentlab | sshfs -o password_stdin -o allow_other student@chips:/home/student/chips chips
