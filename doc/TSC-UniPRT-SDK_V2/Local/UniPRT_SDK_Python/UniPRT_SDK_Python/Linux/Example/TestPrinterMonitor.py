import CommSDK
import JsonSDK
from enum import Enum
from RfidMonitor import RfidReport
from OdvMonitor import OdvReport
import time
import sys


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

class INFO_TYP(Enum):
    ODV_TYP = 0
    RFID_TYP = 1
    PRINTER_TYP = 2


Comm_Sdk_Instance = CommSDK.CommSDK()
Json_Sdk_Instance = JsonSDK.JsonSDK()


class Printer:
    PrtInfo = PrinterInfo()


Printer_Instance = Printer()



def show_printer_info(strIP):
    Json_Sdk_Instance.PrinterMonitorConnection(strIP, INFO_TYP.PRINTER_TYP)
    Json_Sdk_Instance.GetPrinterInfo(Printer_Instance.PrtInfo, INFO_TYP.PRINTER_TYP)

    print("\nPrinter Model:", Printer_Instance.PrtInfo.Model)
    print("Printer SN:", Printer_Instance.PrtInfo.SerialNumber)
    print("Printer FW PN:", Printer_Instance.PrtInfo.FirmwarePartNumber)
    print("Printer FW Ver:", Printer_Instance.PrtInfo.FirmwareVersion)
    print("Printhead Resolution (Dots/Inch):", Printer_Instance.PrtInfo.PrintheadResolution)
    print("\nHas RFID:", "yes" if Printer_Instance.PrtInfo.HasRfidOption else "no")
    print("Has ODV:", "yes" if Printer_Instance.PrtInfo.HasOdvOption else "no")


def ptr_alert_notice_listener(alert):
        # Print out alerts: e.g. "2418" ("Print Head Open" fault/alert)
        # "0000" = no alerts
        print(f"Printer Alert #: \n  {alert[0]} - {alert[1]}\n\n")

    
def ptr_engine_status_notice_listener(engine_state):
    # Print out engine status: e.g. "idle", "offline", "online", "printing"...
    print(f"Engine Status: \n  {engine_state}\n\n")


def ptr_display_status_notice_listener(new_display_text):
    # Print display msgs: e.g. "ONLINE" "ETHERNET/PGL/LP+" or "PRINT HEAD UP" //"Close Print Head"
    print("Printer Display: \n")
    for txt_line in new_display_text:
        print(f"  {txt_line}\n")


def wait_for_something_to_happen_printer_monitor(strIP):
    usage = "\nUsage: \r\n '1' print test file \r\n '0' quit\r\n Enter the number and then press <Enter>. Or, press 0 to exit. "
    print(usage)

    while True:
        choice = input().strip()

        if choice == '0':  # quit/exit
            print(choice)
            return
        elif choice == '1':  # send test print job
            print(choice)
            Comm_Sdk_Instance.SendPrintFile(strIP, "Hello_1.pgl")
        else:
            print(usage)

        time.sleep(0.5)


    
def printer_monitor(strIP):
    try:
        Json_Sdk_Instance.PrinterMonitorConnection(strIP, INFO_TYP.PRINTER_TYP)

        Json_Sdk_Instance.SetAlertStatusListening(True)
        Json_Sdk_Instance.SetAlertStatusCallback(ptr_alert_notice_listener)

        Json_Sdk_Instance.SetEngineStatusListening(True)
        Json_Sdk_Instance.SetEngineStatusCallback(ptr_engine_status_notice_listener)

        Json_Sdk_Instance.SetDisplayStatusListening(True)
        Json_Sdk_Instance.SetDisplayStatusCallback(ptr_display_status_notice_listener)

        wait_for_something_to_happen_printer_monitor(strIP)

    except Exception as e:
        print(f"Exception Msg: {str(e)}")

    Json_Sdk_Instance.PrinterMonitorDispose(INFO_TYP.PRINTER_TYP)


def main():


    ptrIp = "10.0.10.170"
    show_printer_info(ptrIp)

    printer_monitor(ptrIp)

    Comm_Sdk_Instance.Close()


if __name__ == "__main__":
    main()