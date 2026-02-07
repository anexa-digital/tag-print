using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UniPRT.Sdk.Comm;
using UniPRT.Sdk.Settings;

namespace Snippets
{
    class MySettings
    {
        public static void MainSettings(string[] args)
        {
            IComm ptrComm;
            
            //ptrComm = GetUsbConnection();            
            ptrComm = new TcpConnection("192.168.1.50", TcpConnection.DEFAULT_MGMT_PORT);

            ptrComm.Open();
            Console.WriteLine(Environment.NewLine+ "Reading some settings..." + Environment.NewLine);            
            ReadSomePrinterSettings(ptrComm);
            
            Console.WriteLine(Environment.NewLine + "Making Setting Changes..." + Environment.NewLine);
            ChangePrinterSettings(ptrComm);
            ptrComm.Close();
        }

        public static IComm GetUsbConnection()  // Find first Printronix printer connected via USB and return the connection
        {
            UsbConnection PtrUsbComm = null;
            var devices = UsbConnection.AvaliableDevices();
            if (devices.Count > 0)
            {
                Console.WriteLine($"{devices.Count} USB devices found...\r\n");
                for (int i = 0; i < devices.Count; i++)
                {
                    Console.WriteLine($"Device {i}: VendorID= {devices[i].vendorID:X} ProdudctID={devices[i].productID:X}");
                    if (UsbConnection.PTX_USB_VID == devices[i].vendorID)   // Find the vendor ID we are interested in
                    {
                        PtrUsbComm = new UsbConnection(devices[0].vendorID, devices[0].productID);
                        break;
                    }
                }
            }

            return PtrUsbComm;
        }

        public static void ReadSomePrinterSettings(IComm ptrComm)
        {
            try
            {
                if (null != ptrComm)
                {
                    if (!ptrComm.Connected)
                    {
                        Console.WriteLine("Error: no connection");
                        return;
                    }

                    SettingsReadWrite mySettings = new SettingsReadWrite(ptrComm);

                    // Read individual settings if needed
                    Console.WriteLine($"LCD Units: '{mySettings.GetValue("LCD.LabelUnits")}'");
                    Console.WriteLine($"Printer Resolution: '{mySettings.GetValue("Printer.Head.DPI-d")}'");
                    Console.WriteLine($"LCD Language: '{mySettings.GetValue("LCD.Language")}'");

                    // read list of settings
                    Console.WriteLine();
                    Console.WriteLine("Reading label settings:");
                    Dictionary<string, string> contentList = mySettings.GetValues(
                        new List<string>() { 
                        "Handling.Type", 
                        "Image.Length-in", 
                        "Image.Width-in", 
                        "Image.Clip-b", 
                        "Label.Sensor" });
                    foreach (KeyValuePair<string, string> item in contentList)
                    {
                        Console.WriteLine($"\"{item.Key}\" = {item.Value}");
                    }
                    
                    mySettings.Dispose();
                }
            }
            catch (Exception err)
            {
                Console.WriteLine($"Error: {err}");
            }
        }

        public static void ChangePrinterSettings(IComm ptrComm)
        {
            try
            {
                if (null != ptrComm)
                {
                    if (!ptrComm.Connected)
                    {
                        Console.WriteLine("Error: no connection");
                        return;
                    }

                    SettingsReadWrite mySettings = new SettingsReadWrite(ptrComm);

                    // Change units displayed on LCD 
                    //  LCD.MediaUnits can be: eInches, eMetric
                    mySettings.SetValue("LCD.MediaUnits", "\"eInches\"");                    
                    mySettings.SetValue("Image.Length-in", "4.3");

                    // Change list of settings
                    //  Handling.Type can be: eContinuous, eCut, ePeelOff, eTearOff, eTearOffStrip
                    //  Label.Sensor can be: eDisable, eMark, eGap, eAdvNotch, eAdvGap, 
                    Dictionary<string, string> setKeys = 
                        new Dictionary<string, string>() { 
                        { "Handling.Type", "\"eContinuous\"" }, 
                        { "Image.Clip-b", "false" }, 
                        { "Label.Sensor", "\"eGap\"" } };
                    if (mySettings.SetValues(setKeys))
                    {
                        Console.WriteLine("Setvalues SUCCESS.");
                    }
                    else
                    {
                        Console.WriteLine("Setvalues failed.");
                    }

                    Console.WriteLine();
                    Console.WriteLine("Settings read after changes made:");                    
                    Dictionary<string, string> contentList = mySettings.GetValues(new List<string>(setKeys.Keys));
                    foreach (KeyValuePair<string, string> item in contentList)
                    {
                        Console.WriteLine($"\"{item.Key}\" = {item.Value}");
                    }

                    mySettings.Dispose();
                }
            }
            catch (Exception err)
            {
                Console.WriteLine($"Error: {err}");
            }
        }
    }
}