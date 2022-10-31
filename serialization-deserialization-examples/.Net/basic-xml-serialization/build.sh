mcs -out:basic-xml-serializer.exe basic-xml-serializer.cs;
mcs -out:basic-xml-deserializer.exe basic-xml-deserializer.cs -r:basic-xml-serializer.exe;
