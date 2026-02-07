using System;
using System.Collections.Generic;
using UniPRT.Sdk.Monitor;
using UniPRT.Sdk.Reports;

namespace Snippets
{
    public class MyOdvMonitoring
    {
        private static OdvMonitor _odvReportListener = null;

        public static void MainOdvMonitor(string[] args)
        {
            Console.WriteLine("Listening for ODV barcode reports.");
            try
            {
                _odvReportListener = new OdvMonitor("127.0.0.1");

                _odvReportListener.OdvReportListening = true;   // enable parsing of unsolicited barcode report msgs from printer                    
                _odvReportListener.OdvReportCallback = myOdvReportProcessing;  // set the callback/delegate to call when reports received

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
                // release any resources associated with object
                _odvReportListener?.Dispose();
            }
        }
        public static void myOdvReportProcessing(OdvReport odvReport)
        {
            // Could also customize into CSV format based on needs
            string userFriendlyResult = odvReport.Failed ? "failed" : "passed"; // failure output as "failed"/"passed" to make more user friendly
            Console.WriteLine("\r\nShort CSV Format (customized ordered list): pass/fail, Grade, Data");
            Console.WriteLine($"  {userFriendlyResult}, {odvReport.OverallGrade}, {odvReport.Data}");
        }
    }
}
