from UniPRT.Comm.TcpComm import TcpComm
from UniPRT.Json.PrinterMonitor import PrinterMonitor
from UniPRT.Json.SettingsReadWrite import SettingsReadWrite
import threading

IP = "10.0.10.179"


def main():
    ip_address = IP
    tcp_comm = TcpComm(ip_address, 3007)
    tcp_comm.open()
    setting = SettingsReadWrite(connection=tcp_comm)

    printer_monitor = PrinterMonitor(tcp_comm)

    def engine_status_update(status):
        print(f"Engine status update: {status}")

    def display_status_update(status):
        print(f"Display status update: {', '.join(status)}")

    def alert_status_update(status):
        print(f"Alert status update: {', '.join(status)}")

    choice = 0
    while choice != 6:
        print("\nMenu:")
        print("1 - Get Printer Info")
        print("2 - Listen to Engine Status")
        print("3 - Listen to Display Status")
        print("4 - Listen to Alert Status")
        print("5 - Print example file")
        print("6 - Exit")
        choice = int(input("Enter your choice (1-6): ").strip())

        if choice == 1:
            prt_info = printer_monitor.get_printer_info()
            print(f"Printer Model: {prt_info.model()}")
            print(f"Printer SN: {prt_info.serial_number()}")
            print(f"Printer FW PN: {prt_info.firmware_part_number()}")
            print(f"Printer FW Ver: {prt_info.firmware_version()}")
            print(
                f"Printhead Resolution (Dots/Inch): {prt_info.printhead_resolution()}"
            )
            print(f"Has RFID: {'Yes' if prt_info.has_rfid_option() else 'No'}")
            print(f"Has ODV: {'Yes' if prt_info.has_odv_option() else 'No'}")

        elif choice == 2:
            printer_monitor.engine_status_callback = engine_status_update
            engine_thread = threading.Thread(
                target=lambda: printer_monitor.set_engine_status_listening(True)
            )
            engine_thread.daemon = True
            engine_thread.start()

        elif choice == 3:
            printer_monitor.display_status_callback = display_status_update
            display_thread = threading.Thread(
                target=lambda: printer_monitor.set_display_status_listening(True)
            )
            display_thread.daemon = True
            display_thread.start()

        elif choice == 4:
            printer_monitor.alert_status_callback = alert_status_update
            alert_thread = threading.Thread(
                target=lambda: printer_monitor.set_alert_status_listening(True)
            )
            alert_thread.daemon = True
            alert_thread.start()

        elif choice == 5:
            tcp_comm2 = TcpComm(IP, 9100)
            tcp_comm2.open()
            tcp_comm2.send_printer_file(
                IP, "/Users/realbuber/Documents/Project/UniPRT_python/example/Hello.pgl"
            )
            print("Print file sent.")

        elif choice == 6:
            print("Exiting...")

        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
