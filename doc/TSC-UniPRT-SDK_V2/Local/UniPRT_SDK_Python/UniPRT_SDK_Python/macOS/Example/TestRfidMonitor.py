from UniPRT.Comm.TcpComm import TcpComm
from UniPRT.Json.RfidMonitor import RfidMonitor, RfidReport
from UniPRT.Json.PrinterMonitor import PrinterMonitor

import threading

IP = "10.0.10.171"


def main():
    ip_address = IP
    tcp_comm = TcpComm(ipAddress=ip_address, port=3007)
    tcp_comm.open()

    rfid_monitor = RfidMonitor(tcp_comm)
    printer_monitor = PrinterMonitor(tcp_comm)

    choice = 0
    while choice != 4:
        print("\nMenu:")
        print("1 - Get Printer Info")
        print("2 - Listen to RfidReport")
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

            def rfid_report_callback(report: RfidReport):
                if report.failed():
                    print("\nRFID Failed.")
                else:
                    print("\nRFID Passed.")
                    print(
                        f"Write Action: {'Yes' if report.is_write_operation() else 'No'}"
                    )
                    print(f"Data: \n{report.data()}")

            rfid_monitor.rfid_report_callback = rfid_report_callback
            rfid_thread = threading.Thread(
                target=lambda: rfid_monitor.set_rfid_report_listening(True)
            )
            rfid_thread.daemon = True
            rfid_thread.start()

        elif choice == 3:
            tcp_comm2 = TcpComm(ipAddress=IP, port=9100)
            tcp_comm2.send_printer_file(
                IP, "/Users/realbuber/Documents/Example/Python SDK example/rfid.pgl"
            )
            print("Sending RFID print job...")

        elif choice == 4:
            print("Exiting...")

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
