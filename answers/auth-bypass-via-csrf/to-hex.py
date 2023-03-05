import binascii
with open('pg_exec.so', 'rb') as file:
    udf = binascii.hexlify(file.read()).decode('utf-8')
    print(udf)
    #print(len(udf))
    #print(len(udf)/4)
    #print((len(udf)-1)//4096+1)
