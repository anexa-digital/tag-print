from UniPRT.Comm.TcpComm import TcpComm
from UniPRT.Json.PrinterMonitor import PrinterMonitor
from UniPRT.Json.OdvMonitor import OdvMonitor, OdvReport
import threading

IP = "10.0.10.206"


def main():
    ip_address = IP
    tcp_comm = TcpComm(ipAddress=ip_address, port=3007)
    tcp_comm.open()

    odv_monitor = OdvMonitor(tcp_comm)
    printer_monitor = PrinterMonitor(tcp_comm)

    choice = 0
    while choice != 4:
        print("\nMenu:")
        print("1 - Get Printer Info")
        print("2 - Listen to OdvReport")
        print("3 - Print example file")
        print("4 - Exit")
        choice = int(input("Enter your choice (1-4): ").strip())

        if choice == 1:
            printer_info = printer_monitor.get_printer_info()
            print("\n======= RFID Printer Info: ")
            print(f"Printer Model: {printer_info.model()}")
            print(f"Printer SN: {printer_info.serial_number()}")
            print(f"Printer FW PN: {printer_info.firmware_part_number()}")
            print(f"Printer FW Ver: {printer_info.firmware_version()}")
            print(
                f"Printhead Resolution (Dots/Inch): {printer_info.printhead_resolution()}"
            )
            print(f"Has RFID: {'Yes' if printer_info.has_rfid_option else 'No'}")
            print(f"Has ODV: {'Yes' if printer_info.has_odv_option() else 'No'}")

        elif choice == 2:

            def odv_report_callback(report: OdvReport):
                if report.failed():
                    print("\nBarcode Failed.")
                else:
                    print("\nBarcode Passed.")
                    overall_grade = report.overall_grade_as_float()
                    if overall_grade > 3.5:
                        print(
                            f"Print Quality passed. \n Overall Grade= {overall_grade:.2f}"
                        )
                    else:
                        print(
                            f"Print Quality Failed. \n Overall Grade= {overall_grade:.2f}"
                        )

                    print(f"Barcode Symbology: {report.symbology()}")
                    print(f"Barcode Data: {report.data()}")

            odv_monitor.odv_report_callback = odv_report_callback
            threading.Thread(
                target=odv_monitor.set_odv_report_listening, args=(True,)
            ).start()

        elif choice == 3:
            tcp_comm2 = TcpComm(ipAddress=IP, port=9100)
            tcp_comm2.send_printer_file(
                IP,
                "/Users/realbuber/Documents/Project/UniPRT_python/example/DM_PRINTRONIX_1.pgl",
            )
            print("Sending ODV print job...")

        elif choice == 4:
            print("Exiting...")

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
