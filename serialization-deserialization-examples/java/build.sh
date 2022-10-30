sh clean.sh;
javac SerialExample.java DummyObject1.java;
java SerialExample serial.ser;
java -jar ./SerializationDumper-v1.13.jar -r ./serial.ser > dump.txt;
javac DeserialExample.java DummyObject1.java
java DeserialExample serial.ser;
echo 'Play with the values in dump.txt and then use the command below to rebuilt the modified object.'
echo "For instance we can change the value of b from 1000 to 2000 with: sed -i 's/(int)1000 - 0x00 00 03 e8/(int)1000 - 0x00 00 07 D0/g' dump.txt";
echo 'java -jar SerializationDumper-v1.13.jar -b dump.txt serial-modified.ser;java DeserialExample serial-modified.ser'