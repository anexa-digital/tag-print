import CommSDK
import JsonSDK
from RfidMonitor import RfidReport
import threading
import time


class PrinterInfo:
    def __init__(self, model="", serial_number="", firmware_part_number="", firmware_version="", printhead_resolution="",
                 has_rfid_option="", has_odv_option=""):
        self.Model = model
        self.SerialNumber = serial_number
        self.FirmwarePartNumber = firmware_part_number
        self.FirmwareVersion = firmware_version
        self.PrintheadResolution = printhead_resolution
        self.HasRfidOption = has_rfid_option
        self.HasOdvOption = has_odv_option


ODV_TYP = 0
RFID_TYP = 1
PRINTER_TYP = 2


Comm_Sdk_Instance = CommSDK.CommSDK()
Json_Sdk_Instance = JsonSDK.JsonSDK()


def ShowPrinterInfo(p_prt_info: PrinterInfo, INFO_TYP):

    Json_Sdk_Instance.GetPrinterInfo(p_prt_info, INFO_TYP)

    print()
    print("Printer Model:", p_prt_info.Model)
    print("Printer SN:", p_prt_info.SerialNumber)
    print("Printer FW PN:", p_prt_info.FirmwarePartNumber)
    print("Printer FW Ver:", p_prt_info.FirmwareVersion)
    print("Printhead Resolution (Dots/Inch):", p_prt_info.PrintheadResolution)
    print()
    print("Has RFID:", "yes" if p_prt_info.HasRfidOption else "no")
   



def RfidReportCallback(report: RfidReport):

    print_lock = threading.Lock()
    with print_lock:
        if report.Failed():
            print("\nRFID Failed.")
        else:
            memory_type = ""
            data_type = report.DataType()
            
            if data_type == RfidReport.RfidDataType.USR:
                memory_type = "USR"
            elif data_type == RfidReport.RfidDataType.TID:
                memory_type = "TID"
            elif data_type == RfidReport.RfidDataType.UNKNOWN:
                memory_type = "UNKNOWN"

            print("\nRFID Passed.")
            print("Write Action:", "yes" if report.IsWriteOperation() else "no")
            print("Operation on EPC Memory:", "yes" if data_type == RfidReport.RfidDataType.EPC else "no")

            if data_type != RfidReport.RfidDataType.EPC:
                print("  memory accessed:", memory_type)

            print("Data:\n", report.Data())


def Dispose():
    Json_Sdk_Instance.RfidMonitorDispose()
    Json_Sdk_Instance.PrinterMonitorDispose(RFID_TYP)
    Comm_Sdk_Instance.Close()




def main():
    ptr_ip_rfid = "10.0.10.172"
    prt_info = PrinterInfo()

    Json_Sdk_Instance.RfidMonitorConnection(ptr_ip_rfid)
    Json_Sdk_Instance.PrinterMonitorConnection(ptr_ip_rfid, RFID_TYP)


    try:
        print("\n=======Rfid Printer Info: ")
        ShowPrinterInfo(prt_info, RFID_TYP)


        if not prt_info.HasRfidOption:
            print("WARNING: Missing RFID option on printer at:", ptr_ip_rfid)

        Json_Sdk_Instance.SetRfidReportListening(True)
        Json_Sdk_Instance.SetRfidReportCallback(RfidReportCallback)


        Comm_Sdk_Instance.SendPrintFile(ptr_ip_rfid, "rfid.pgl")
        print("Sending RFID print job...")


        userInput = None

        # 循環等待用戶輸入，直到用戶輸入0為止
        
        while userInput != 0:
            print("\nPress 0 to exit")
            userInput = int(input())
            time.sleep(0.5)

        # 使用者輸入0 後程式結束
        print("\nProgram exit\n")

    except Exception as ex:
        print("Exception:", str(ex))

    finally:
        Dispose()



if __name__ == "__main__":
    main()