import CommSDK
import JsonSDK
from OdvMonitor import OdvReport
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
    print("Has ODV:", "yes" if p_prt_info.HasOdvOption else "no")



def OdvReportCallback(report : OdvReport):
    if report.Failed():
        print("\nBarcode Failed.")
    else:
        print("\nBarcode Passed.")
        print("Grade:", report.OverallGrade())

        if report.OverallGradeAsFloat() > 3.5:
            print("Print Quality passed. \n  Overall Grade =", str(report.OverallGradeAsFloat()))
        else:
            print("Print Quality Failed. \n  Overall Grade =", str(report.OverallGradeAsFloat()))

        print("Barcode Symbology:", report.Symbology())
        print("Barcode Data:", report.Data())



def Dispose():
    Json_Sdk_Instance.OdvMonitorDispose()
    Json_Sdk_Instance.PrinterMonitorDispose(ODV_TYP)
    Comm_Sdk_Instance.Close()




def main():
    ptr_ip_odv = "10.0.10.181"
    prt_info = PrinterInfo()

    Json_Sdk_Instance.OdvMonitorConnection(ptr_ip_odv)
    Json_Sdk_Instance.PrinterMonitorConnection(ptr_ip_odv, ODV_TYP)


    try:
        print("\n=======Odv Printer Info: ")
        ShowPrinterInfo(prt_info, ODV_TYP)


        if not prt_info.HasOdvOption:
            print("WARNING: Missing ODV option on printer at:", ptr_ip_odv)

        Json_Sdk_Instance.SetOdvReportListening(True)
        Json_Sdk_Instance.SetOdvReportCallback(OdvReportCallback)


        Comm_Sdk_Instance.SendPrintFile(ptr_ip_odv, "DM_PRINTRONIX_1.pgl")
        print("Sending datamatrix barcode print job...")


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