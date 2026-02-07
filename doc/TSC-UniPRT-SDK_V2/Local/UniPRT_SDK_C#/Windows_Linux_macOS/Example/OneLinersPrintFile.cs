using System;
using System.IO;
using System.Text;
using UniPRT.Sdk.Utilities;    

namespace OnelinerSnippet
{
    class SendPrintFile
    {
        public static void MainSendPrintFile(string[] args)
        {
            string ptrIp = "192.168.1.53";
            string fileToSend = @"C:\testFiles\Hello.pgl";
            Utilities.SendPrintFile(ptrIp, fileToSend);             // Using SDK  Utilties to send print job
        }
    }
}
