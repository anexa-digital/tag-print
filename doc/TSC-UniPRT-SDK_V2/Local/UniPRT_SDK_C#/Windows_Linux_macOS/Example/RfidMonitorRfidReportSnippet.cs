using System;
using UniPRT.Sdk.Monitor;
using UniPRT.Sdk.Reports;

namespace Snippets
{
    public class MyRfidMonitoring
    {                
        private static RfidMonitor _rfidReportListener = null;

        public static void MainRfidMonitor(string[] args)
        {
            Console.WriteLine("Listening for RFID reports.");
            try
            {
                _rfidReportListener = new RfidMonitor("127.0.0.1");

                _rfidReportListener.RfidReportListening = true;   // enable parsing of unsolicited barcode report msgs from printer                    
                _rfidReportListener.RfidReportCallback = myReportProcessing;  // set the callback/delegate to call when reports received

                while (true)   // wait for something to happen
                {
                    // pretend to be busy doing some other work here...
                }
            }

            catch (Exception e)
            {
                Console.WriteLine($"Exception Msg: {e.Message}");
            }
            finally
            {
                _rfidReportListener?.Dispose();
            }
        }
        public static void myReportProcessing(RfidReport report)
        {
            // this function called when RFID reports received.
            // Here we can read and use any part of the report as needed.
            // In our case, simply printing report contents to console but could write to file for archiving if needed

            if (report.Failed)
            {
                Console.WriteLine("\nRFID Failed.");
            }
            else
            {
                string memoryType = "";
                switch (report.DataType)
                {
                    case RfidReport.RfidDataType.USR:
                        memoryType = "USR";
                        break;
                    case RfidReport.RfidDataType.TID:
                        memoryType = "TID";
                        break;
                    case RfidReport.RfidDataType.UNKNOWN:
                        memoryType = "UNKNOWN";
                        break;
                }


                Console.WriteLine("\nRFID Passed.");
                Console.WriteLine($"Write Action: {((report.IsWriteOperation) ? "yes" : "no")}");
                Console.WriteLine($"Operation on EPC Memory: {((report.DataType == RfidReport.RfidDataType.EPC) ? "yes" : "no")}");
                if (report.DataType != RfidReport.RfidDataType.EPC)
                {
                    Console.WriteLine($"  memory accessed: {memoryType}");
                }

                Console.WriteLine($"Data: \n {report.Data}");
            }
        }
    }
}
