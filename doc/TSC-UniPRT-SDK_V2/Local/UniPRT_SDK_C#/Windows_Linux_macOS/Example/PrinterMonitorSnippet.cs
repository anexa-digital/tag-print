using System;
using UniPRT.Sdk.Monitor;

namespace Snippets
{
    public class MyPrinterMonitoring
    {
        // setup a comm and xml parser for listening to xml msgs from printer
        private static PrinterMonitor _PrinterMntr = null;

        public static void MainPrinterMonitor(string[] args)
        {
            Console.WriteLine("Monitoring Printer.");
            try
            {
                _PrinterMntr = new PrinterMonitor("192.168.1.57");

                // setup for listening for alerts
                _PrinterMntr.AlertStatusListening = true;     // enable unsolicited alert status msgs from printer
                _PrinterMntr.AlertStatusCallback = PtrAlertNoticeListener;

                // setup for listening for Engine Status
                _PrinterMntr.EngineStatusListening = true;     // enable unsolicited engine status msgs from printer
                _PrinterMntr.EngineStatusCallback = PtrEngineStatusNoticeListener;

                // setup for listening for display text msgs
                _PrinterMntr.DisplayStatusListening = true;     // enable unsolicited display text msgs from printer
                _PrinterMntr.DisplayStatusCallback = PtrDisplayStatusNoticeListener;

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
                _PrinterMntr?.Dispose();
            }
        }

        private static void PtrAlertNoticeListener(string[] newAlertText)
        {
            // Print out alerts: e.g. "2418" ("Print Head Open" fault/alert)
            Console.WriteLine($"Printer Alert #: \r\n  {newAlertText[0]} - {newAlertText[1]}\r\n");
        }
        private static void PtrEngineStatusNoticeListener(string newEngineStatus)
        {
            // Print out engine status: e.g. "idle", "offline", "online", "printing"...
            Console.WriteLine($"Engine Status: \r\n  {newEngineStatus} \r\n");
        }
        private static void PtrDisplayStatusNoticeListener(string[] newDisplayText)
        {
            // Print display msgs: e.g. "ONLINE" "ETHERNET/PGL/LP+" or "PRINT HEAD UP" "Close Print Head"
            Console.WriteLine("Printer Display: ");
            foreach (string txtLine in newDisplayText)
            {
                Console.WriteLine($"  {txtLine}");
            }
        }

    }
}
