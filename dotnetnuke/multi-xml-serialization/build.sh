mcs -out:multi-xml-serializer.exe multi-xml-serializer.cs;
mcs -out:multi-xml-deserializer.exe multi-xml-deserializer.cs -r:multi-xml-serializer.exe;
