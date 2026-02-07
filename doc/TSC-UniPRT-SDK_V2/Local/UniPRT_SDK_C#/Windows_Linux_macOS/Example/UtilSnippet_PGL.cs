using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using UniPRT.Sdk.Comm;
using UniPRT.Sdk.LabelMaker.PGL;
using UniPRT.Sdk.LabelMaker.Interfaces;
using UniPRT.Sdk.LabelMaker.PglLib;  // imports SDK namespace

namespace Snippets
{
    class MyLabel
    {
        public static void MainComm(string[] args)
        {
            byte[] download = PGL_Utilities.WindowsFont("TMP", 50, 0, 3, "Arial", "TestString");
            UniPRT.Sdk.LabelMaker.PGL.Label lbl = new UniPRT.Sdk.LabelMaker.PGL.Label("PictureLabel");
            Picutre picutre = new Picutre(new Point(0f, 0f), "TMP");
            lbl.AddObject(picutre);
            string str = lbl.ToString();
            Console.WriteLine(str);

            //var comm = new TcpConnection("192.168.101.56", 9100);
            var comm = new UsbConnection();
            comm.Open();
            if (comm.Connected)
            {
                comm.Write(download);
                comm.Write(Encoding.UTF8.GetBytes(str));
            }
            comm.Close();       
        }

    }
}