from UniPRT.PrinterDiscovery.printer_discovery import NetworkDiscover, PrinterBrand
import asyncio

discovery = asyncio.run(
    NetworkDiscover.get_printer_list_with_brand(PrinterBrand.TSC, timeout_ms=4000)
)


discovery_all_printers = NetworkDiscover.get_printer_list()
print(discovery)
print(discovery_all_printers)


input("Press Enter to exit...")
