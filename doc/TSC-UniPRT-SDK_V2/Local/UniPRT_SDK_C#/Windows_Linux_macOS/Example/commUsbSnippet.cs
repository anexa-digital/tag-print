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
            SendPrintFile();     // send file over usb
            SendPrintString();   // send print data over usb           
        }

        public static void SendPrintFile()  // send file over usb
        {
            var devices = UsbConnection.AvaliableDevices();
            if (devices.Count > 0)
            {
                string fileName = @"C:\testFiles\Hello.pgl";
                UsbConnection PtrUsbComm = new UsbConnection(devices[0].vendorID, devices[0].productID);
                try
                {
                    PtrUsbComm.Open();
                    if (File.Exists(fileName))
                    {
                        using (BinaryReader binReader = new BinaryReader(File.Open(fileName, FileMode.Open)))
                        {
                            Console.WriteLine($"Sending \"{fileName}\" to printer");
                            PtrUsbComm.Write(binReader);
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
                    PtrUsbComm.Close();
                }
            }
        }

        public static void SendPrintString()    // send print data over usb
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
            var devices = UsbConnection.AvaliableDevices();
            if (devices.Count > 0)
            {
                UsbConnection PtrUsbComm = new UsbConnection(devices[0].vendorID, devices[0].productID);

                try
                {
                    PtrUsbComm.Open();

                    if (PtrUsbComm.Connected)
                    {
                        //byte[] outBytes = Encoding.UTF8.GetBytes(dataToPrint);
                        byte[] outBytes = Encoding.ASCII.GetBytes(dataToPrint);
                        PtrUsbComm.Write(outBytes);
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
                    PtrUsbComm.Close();
                }
            }
        }
    }
}