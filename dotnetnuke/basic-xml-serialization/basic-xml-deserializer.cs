using System.IO;
using System.Xml.Serialization;
using BasicXMLSerializer;
namespace BasicXMLDeserializer
{
    class Program
    {
        static void Main(string[] args)
        {
            var fileStream = new FileStream(args[0], FileMode.Open, FileAccess.Read);
            var streamReader = new StreamReader(fileStream);
            XmlSerializer serializer = new XmlSerializer(typeof(MyConsoleText));
            serializer.Deserialize(streamReader);
        }
    }
}
