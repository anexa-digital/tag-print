#!/usr/bin/env python3.8
"""
RFID Tag Printer - Printronix T820 (Python / WSL)

Programa de consola para impresión de etiquetas RFID.
Usando ZPL (modo ZGL) + UniPRT SDK Python para conexión.

ANTES DE EJECUTAR:
1. Cambiar lenguaje de impresora a ZGL:
   Settings > Application > Control > Active IGP Emul > ZGL
   (TGL NO soporta RFID - solo ZGL y PGL tienen comandos RFID)
2. Verificar IP de la impresora (default: 192.168.3.38)
3. Ejecutar desde WSL con el SDK configurado (ver README.md)
"""

import sys
import os

# Asegurar que el directorio actual está en el path para imports locales
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rfid_printer_service import RfidPrinterService
from epc_encoder import encode_dispatch_code, decode_epc, normalize_epc

# ============================================
# CONFIGURACIÓN - MODIFICAR SEGÚN TU ENTORNO
# ============================================

PRINTER_IP = "192.168.3.38"
PRINTER_PORT = 9100

# ============================================
# DATOS DE PRUEBA
# ============================================

TEST_EPC = "000000000000000000000001"
TEST_LABEL_TEXT = "RFID TEST - EMPACOR"
TEST_BARCODE = "7501234567890"

# ============================================
# INSTANCIA GLOBAL
# ============================================

printer: RfidPrinterService = None


def print_header():
    print("=" * 60)
    print("     RFID Tag Printer - Printronix T820 (Python/WSL)")
    print("     Modo: ZGL (ZPL) + UniPRT SDK Python")
    print("=" * 60)
    print()


def print_menu():
    print()
    if printer and printer.is_connected:
        print(f"  Estado: {printer.get_status()}")
    else:
        print("  Estado: No conectado")
    print()
    print("Opciones:")
    print("  1. Conectar por Ethernet (TCP/IP)")
    print("  2. Conectar por USB")
    print("  3. Calibrar media (IMPORTANTE tras cambiar a ZGL)")
    print("  4. Imprimir etiqueta de prueba ZPL (sin RFID)")
    print("  5. Imprimir etiqueta RFID - ZPL completo (texto+barcode+RFID)")
    print("  6. Imprimir etiqueta RFID - ZPL minimo (solo RFID encode)")
    print("  7. Imprimir etiqueta RFID con EPC personalizado")
    print("  8. Codificar codigo de despacho a EPC")
    print("  9. Desconectar")
    print("  m. Enviar comando ZPL manual")
    print("  d. Decodificar EPC hex a codigo de despacho")
    print("  0. Salir")
    print()


def require_connection() -> bool:
    """Verifica que hay conexión activa."""
    if printer is None or not printer.is_connected:
        print("  No hay conexion. Use opcion 1 o 2 para conectar.")
        return False
    return True


# ============================================
# OPCIONES DEL MENÚ
# ============================================

def connect_ethernet():
    global printer
    if printer:
        printer.disconnect()

    ip_input = input(f"  IP de la impresora [{PRINTER_IP}]: ").strip()
    ip = ip_input if ip_input else PRINTER_IP

    printer = RfidPrinterService()
    if printer.connect_ethernet(ip, PRINTER_PORT):
        print("  Conexion Ethernet exitosa!")
    else:
        print("  No se pudo conectar. Verifica:")
        print("    - Que la impresora este encendida y ONLINE")
        print("    - Que el lenguaje este en ZGL (no TGL ni PGL)")
        print(f"    - Que la IP {ip} sea correcta")
        print("    - Que el puerto 9100 este abierto")
        print("    - Que WSL tenga acceso a la red local")


def connect_usb():
    global printer
    if printer:
        printer.disconnect()

    print("  Buscando impresoras USB...")
    printer = RfidPrinterService()
    
    # Nota: USB desde WSL puede requerir configuración adicional (usbipd)
    print("  NOTA: USB desde WSL requiere usbipd-win para pasar dispositivos USB.")
    print("  Si falla, usa la conexion Ethernet (opcion 1).")
    print()

    idx_input = input("  Indice del dispositivo USB [0]: ").strip()
    idx = int(idx_input) if idx_input.isdigit() else 0

    if printer.connect_usb(idx):
        print("  Conexion USB exitosa!")
    else:
        print("  No se pudo conectar por USB. Verifica:")
        print("    - Que la impresora este conectada por USB")
        print("    - Que usbipd haya pasado el dispositivo a WSL")
        print("    - Que la impresora este encendida y ONLINE")


def calibrate_media():
    if not require_connection():
        return

    print("  Calibrando media...")
    print("    La impresora avanzara algunas etiquetas para detectar el gap.")
    print("    Esto es NECESARIO tras cambiar de TGL a ZGL.")
    print()

    if printer.calibrate_media():
        print("  Calibracion enviada. Espera a que la impresora termine de avanzar.")


def print_simple_test():
    if not require_connection():
        return

    print("  Imprimiendo etiqueta de prueba simple...")
    if printer.print_test_label("TEST CONEXION"):
        print("  Etiqueta enviada. Verifica que se imprimio.")


def print_rfid_full():
    if not require_connection():
        return

    print(f"  [ZPL Completo] RFID + texto + barcode")
    print(f"    EPC: {TEST_EPC}")
    print(f"    Texto: {TEST_LABEL_TEXT}")
    print(f"    Codigo: {TEST_BARCODE}")
    print()

    if printer.print_rfid_label(TEST_EPC, TEST_LABEL_TEXT, TEST_BARCODE):
        print()
        print("  Etiqueta RFID enviada!")
        print("  Verifica con un lector RFID que el EPC se escribio correctamente.")


def print_rfid_minimal():
    if not require_connection():
        return

    print(f"  [ZPL Minimo] Solo RFID encode - para depuracion")
    print(f"    EPC: {TEST_EPC}")
    print()

    if printer.print_rfid_label_raw(TEST_EPC):
        print()
        print("  Etiqueta RFID enviada!")
        print("  Verifica con un lector RFID que el EPC se escribio correctamente.")


def print_rfid_custom():
    if not require_connection():
        return

    print("  Ingresa los datos para la etiqueta RFID:")
    print()

    epc = input(f"    EPC (24 chars hex, ej: E20034120123456789ABCDEF): ").strip()
    if not epc:
        epc = TEST_EPC

    text = input(f"    Texto de etiqueta: ").strip()
    if not text:
        text = "CUSTOM RFID"

    barcode = input(f"    Codigo de barras: ").strip()
    if not barcode:
        barcode = "123456789"

    print()
    print(f"  Imprimiendo con EPC: {epc}")

    if printer.print_rfid_label(epc, text, barcode):
        print("  Etiqueta RFID personalizada enviada!")


def encode_dispatch():
    """Codifica un código de despacho Empacor a EPC hex."""
    print("  Codificador de codigo de despacho a EPC")
    print("  Formato: TIPO_DOC-NUMERO1-TIPO_UBIC-NUMERO2")
    print("  Ejemplo: PVE-219836-WAR-3270806")
    print()

    code = input("  Codigo de despacho: ").strip()
    if not code:
        print("  Cancelado.")
        return

    epc = encode_dispatch_code(code)
    if epc:
        print()
        print(f"  Codigo:  {code}")
        print(f"  EPC hex: {epc}")
        print()
        
        if printer and printer.is_connected:
            send = input("  Imprimir etiqueta RFID con este EPC? (s/N): ").strip().lower()
            if send == 's':
                text = input(f"    Texto de etiqueta [{code}]: ").strip()
                if not text:
                    text = code
                barcode = input(f"    Codigo de barras []: ").strip()
                if not barcode:
                    barcode = code.replace("-", "")
                
                printer.print_rfid_label(epc, text, barcode)


def decode_epc_hex():
    """Decodifica un EPC hex a código de despacho Empacor."""
    print("  Decodificador de EPC hex a codigo de despacho")
    print()

    epc = input("  EPC hex (24 chars): ").strip()
    if not epc:
        print("  Cancelado.")
        return

    code = decode_epc(epc)
    if code:
        print()
        print(f"  EPC hex: {epc.upper()}")
        print(f"  Codigo:  {code}")
    else:
        print("  No se pudo decodificar el EPC.")


def disconnect_printer():
    global printer
    if printer:
        printer.disconnect()
        printer = None
    else:
        print("  No hay conexion activa")


def send_manual_command():
    if not require_connection():
        return

    print("  Ingrese el comando ZPL (o 'test' para un comando de prueba):")
    command = input("  > ").strip()

    if command.lower() == "test":
        command = "^XA^PW640^LL160^MNY^FO20,20^A0N,30,30^FDTEST MANUAL ZPL^FS^PQ1^XZ"
        print(f"  Enviando comando de prueba:")
        print(f"  {command}")

    if command:
        if printer.send_raw_command(command):
            print("  Comando enviado!")


# ============================================
# MAIN
# ============================================

def main():
    print_header()

    running = True
    while running:
        print_menu()
        choice = input("Seleccione opcion: ").strip().lower()
        print()

        if choice == '1':
            connect_ethernet()
        elif choice == '2':
            connect_usb()
        elif choice == '3':
            calibrate_media()
        elif choice == '4':
            print_simple_test()
        elif choice == '5':
            print_rfid_full()
        elif choice == '6':
            print_rfid_minimal()
        elif choice == '7':
            print_rfid_custom()
        elif choice == '8':
            encode_dispatch()
        elif choice == '9':
            disconnect_printer()
        elif choice == 'm':
            send_manual_command()
        elif choice == 'd':
            decode_epc_hex()
        elif choice == '0':
            running = False
        else:
            print("  Opcion no valida")

    if printer:
        printer.disconnect()
    print("Programa terminado")


if __name__ == "__main__":
    main()
