using System;
using System.IO;
using System.Text;
using UniPRT.Sdk.Comm;  // imports SDK namespace

namespace Snippets
{
    class MyComm
    {
        public static void MainComm(string[] args)
        {
            string prtIp = "127.0.0.1";
            SendPrintFile(prtIp);     // send file over default printer data port
            SendPrintString(prtIp);   // send print data over default printer data port            
        }

        public static void SendPrintFile(string ipAddress)  // send file over default printer data port
        {
            string fileName = @"C:\testFiles\Hello.pgl";
            TcpConnection PtrTcpComm = new TcpConnection(ipAddress, TcpConnection.DEFAULT_DATA_PORT); // sending through default data port

            try
            {
                PtrTcpComm.Open();
                if (File.Exists(fileName))
                {
                    using (BinaryReader binReader = new BinaryReader(File.Open(fileName, FileMode.Open)))
                    {
                        Console.WriteLine($"Sending \"{fileName}\" to printer");
                        PtrTcpComm.Write(binReader);
                    }
                }
                else
                {
                    Console.WriteLine($"File \"{fileName}\" not found");
                }
            }
            catch (Exception e)
            {
                Console.WriteLine($"Exception Msg: {e.Message}");
            }

            finally
            {
                PtrTcpComm.Close();
            }
        }

        public static void SendPrintString(string ipAddress)    // send print data over default printer data port
        {
            string dataToPrint =
@"~CREATE;C39;72
SCALE;DOT
PAGE;30;40
ALPHA
C10;1;33;0;0;@HELLO@
C16;54;37;0;0;@*World*@
STOP
BARCODE
C128C;XRD3:3:6:6:9:9:12:12;H6;10;32
@World@
STOP
END
~EXECUTE;C39
~NORMAL

";
            TcpConnection PtrTcpComm = new TcpConnection(ipAddress, TcpConnection.DEFAULT_DATA_PORT); // sending through default data port 9100

            try
            {
                PtrTcpComm.Open();

                if (PtrTcpComm.Connected)
                {
                    //byte[] outBytes = Encoding.UTF8.GetBytes(dataToPrint);
                    byte[] outBytes = Encoding.ASCII.GetBytes(dataToPrint);
                    PtrTcpComm.Write(outBytes);
                }
                else
                {
                    Console.WriteLine($"Not connected to printer");
                }
            }
            catch (Exception e)
            {
                Console.WriteLine($"Exception Msg: {e.Message}");
            }

            finally
            {
                PtrTcpComm.Close();
            }
        }
    }
}
