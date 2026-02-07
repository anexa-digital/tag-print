"""
Servicio para impresión de etiquetas RFID en Printronix T820
Usando ZPL (modo ZGL) + UniPRT SDK Python (conexión)

IMPORTANTE: La impresora DEBE estar en modo ZGL (ZPL emulation).
TGL NO soporta comandos RFID. ZGL sí (^RF, ^RB, ^RS, etc.)

Configurar en la impresora:
  Settings > Application > Control > Active IGP Emul > ZGL
"""

import sys
import os
import ctypes

# Agregar el directorio del SDK al path de Python
# Se busca en orden:
#   1. Variable de entorno UNIPRT_SDK_PATH
#   2. sdk_libs/ local (creado por setup_sdk.sh)
#   3. Ruta relativa al SDK original en doc/
SDK_PATH = os.environ.get("UNIPRT_SDK_PATH")
if not SDK_PATH:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _sdk_local = os.path.join(_script_dir, "sdk_libs")
    if os.path.isdir(_sdk_local):
        SDK_PATH = _sdk_local
    else:
        # Fallback: ruta al SDK original
        _project_root = os.path.dirname(_script_dir)
        SDK_PATH = os.path.join(
            _project_root,
            "doc", "TSC-UniPRT-SDK_V2", "Local",
            "UniPRT_SDK_Python", "UniPRT_SDK_Python",
            "Linux", "SDK", "x64"
        )

if os.path.isdir(SDK_PATH):
    if SDK_PATH not in sys.path:
        sys.path.insert(0, SDK_PATH)
    # También agregar al LD_LIBRARY_PATH para que las .so se encuentren
    ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    if SDK_PATH not in ld_path:
        os.environ["LD_LIBRARY_PATH"] = f"{SDK_PATH}:{ld_path}"
else:
    print(f"ADVERTENCIA: Directorio SDK no encontrado: {SDK_PATH}")
    print("  Configura la variable de entorno UNIPRT_SDK_PATH o ejecuta setup_sdk.sh")

try:
    import CommSDK
except ImportError as e:
    print(f"ERROR: No se pudo importar CommSDK: {e}")
    print(f"  SDK Path: {SDK_PATH}")
    print(f"  sys.path incluye SDK: {SDK_PATH in sys.path}")
    print("  Asegúrate de ejecutar desde WSL con las librerías .so en el path.")
    sys.exit(1)

from epc_encoder import normalize_epc
from typing import Optional, List, Tuple


# ============================================
# CONSTANTES DE ETIQUETA (ZPL)
# ============================================

# Dimensiones reales de la etiqueta RFID
# Medidas físicas: 80mm ancho x 20mm alto, gap 3mm, margen derecho 5mm
# ZPL usa dots. A 203 dpi: 1mm = 203/25.4 ≈ 8 dots
LABEL_WIDTH_DOTS = 640    # 80mm @ 203dpi
LABEL_HEIGHT_DOTS = 160   # 20mm @ 203dpi
GAP_DOTS = 24             # 3mm gap @ 203dpi
RIGHT_MARGIN_DOTS = 40    # 5mm margen derecho @ 203dpi
PRINTABLE_WIDTH_DOTS = LABEL_WIDTH_DOTS - RIGHT_MARGIN_DOTS  # 600 dots (75mm)


# ============================================
# ESTRUCTURA USB
# ============================================

class UsbTuple(ctypes.Structure):
    """Estructura C para identificar dispositivos USB"""
    _pack_ = 1
    _fields_ = [
        ("vendorId", ctypes.c_ushort),
        ("productId", ctypes.c_ushort),
    ]


TSC_USB_VID = 0x1203
PTX_USB_VID = 0x14AE


# ============================================
# SERVICIO DE IMPRESORA RFID
# ============================================

class RfidPrinterService:
    """
    Servicio para impresión de etiquetas RFID en Printronix T820.
    
    Usa el SDK UniPRT Python para la conexión (TCP/USB)
    y envía comandos ZPL raw para RFID y contenido visual.
    """

    def __init__(self):
        self._comm = CommSDK.CommSDK()
        self._connected = False
        self._connection_type = ""
        self._connection_info = ""

    # ==========================================
    # CONEXIÓN
    # ==========================================

    def connect_ethernet(self, ip: str, port: int = 9100) -> bool:
        """Conecta a la impresora por TCP/IP (Ethernet)."""
        try:
            print(f"  Conectando a {ip}:{port}...")
            self._comm.TcpConnection(ip, port)
            self._comm.Open()
            
            if self._comm.Connected():
                self._connected = True
                self._connection_type = "Ethernet"
                self._connection_info = f"{ip}:{port}"
                print(f"  Conexión Ethernet establecida")
                return True
            else:
                print("  No se pudo conectar")
                return False
        except Exception as e:
            print(f"  Error de conexión: {e}")
            self._connected = False
            return False

    def connect_usb(self, device_index: int = 0) -> bool:
        """Conecta a la impresora por USB."""
        try:
            print("  Buscando impresoras USB...")
            devices, count = self._comm.GetAvailableDevices()
            
            if count == 0:
                print("  No se encontraron impresoras USB")
                return False
            
            print(f"  Encontrados {count} dispositivo(s):")
            for i in range(count):
                vid = devices[i].vendorId
                pid = devices[i].productId
                brand = "TSC" if vid == TSC_USB_VID else ("Printronix" if vid == PTX_USB_VID else "Otro")
                print(f"    [{i}] {brand} VID:0x{vid:04X} PID:0x{pid:04X}")
            
            if device_index < 0 or device_index >= count:
                print(f"  Índice USB inválido: {device_index}")
                return False
            
            usb_tuple = UsbTuple()
            usb_tuple.vendorId = devices[device_index].vendorId
            usb_tuple.productId = devices[device_index].productId
            
            print(f"  Conectando USB VID:0x{usb_tuple.vendorId:04X} PID:0x{usb_tuple.productId:04X}...")
            self._comm.UsbConnection(usb_tuple)
            self._comm.Open()
            
            if self._comm.Connected():
                self._connected = True
                self._connection_type = "USB"
                self._connection_info = f"VID:0x{usb_tuple.vendorId:04X} PID:0x{usb_tuple.productId:04X}"
                print(f"  Conexión USB establecida")
                return True
            else:
                print("  No se pudo conectar por USB")
                return False
        except Exception as e:
            print(f"  Error de conexión USB: {e}")
            self._connected = False
            return False

    @property
    def is_connected(self) -> bool:
        """Verifica si hay conexión activa."""
        if not self._connected:
            return False
        try:
            return self._comm.Connected()
        except:
            return False

    def get_status(self) -> str:
        """Retorna estado de conexión como string."""
        if self.is_connected:
            return f"Conectado ({self._connection_type}): {self._connection_info}"
        return "No conectado"

    # ==========================================
    # ENVÍO DE DATOS
    # ==========================================

    def _send_command(self, command: str) -> bool:
        """Envía un string como bytes a la impresora."""
        if not self.is_connected:
            print("  Error: No conectado a la impresora")
            return False
        try:
            data = bytearray(command.encode('utf-8'))
            self._comm.Write(data, len(data))
            return True
        except Exception as e:
            print(f"  Error enviando datos: {e}")
            return False

    # ==========================================
    # IMPRESIÓN RFID - ZPL COMPLETO
    # ==========================================

    def print_rfid_label(self, epc_hex: str, label_text: str, barcode_data: str) -> bool:
        """
        Imprime etiqueta RFID con ZPL completo: RFID encode + texto + barcode.
        
        REQUIERE: Impresora en modo ZGL
        
        Memoria EPC (Bank 01):
          Word 0: CRC (auto-calculado por el tag)
          Word 1: PC (Protocol Control)
          Words 2-7: EPC data (96 bits = 6 words = 12 bytes = 24 hex chars)
        
        ^RFW,H,2,12 = Write, Hex, word 2 (después CRC+PC), 12 bytes
        """
        if not self.is_connected:
            print("  Error: No conectado a la impresora")
            return False

        epc_hex = normalize_epc(epc_hex)
        if epc_hex is None:
            return False

        epc_bytes = len(epc_hex) // 2  # 24 hex chars = 12 bytes

        print(f"  [ZPL + RFID] Preparando etiqueta RFID...")
        print(f"    EPC: {epc_hex} ({epc_bytes} bytes)")
        print(f"    Texto: {label_text}")
        print(f"    Código: {barcode_data}")

        try:
            zpl = (
                "^XA"                                               # Inicio formato
                f"^PW{LABEL_WIDTH_DOTS}"                            # Ancho: 640 dots (80mm)
                f"^LL{LABEL_HEIGHT_DOTS}"                           # Alto: 160 dots (20mm)
                "^MNY"                                              # Gap sensing
                # --- RFID Config ---
                "^RS8,0,0,0,0,0"                                    # RFID setup: adaptive antenna
                "^RR3"                                              # 3 reintentos si falla encode
                # --- RFID: Escribir EPC ---
                f"^RFW,H,2,{epc_bytes}^FD{epc_hex}^FS"             # Write EPC
                # --- Contenido visual ---
                f"^FO16,8^A0N,32,24^FD{label_text}^FS"             # Texto grande arriba
                f"^FO16,48^A0N,20,16^FDEPC: {epc_hex}^FS"          # EPC debajo
                f"^FO16,76^BCN,30,Y,N,N^FD{barcode_data}^FS"       # Barcode (Code128)
                "^PQ1"                                              # 1 etiqueta
                "^XZ"                                               # Fin formato
            )

            print(f"\n  Script ZPL enviado:")
            print(f"  ---")
            print(f"  {zpl}")
            print(f"  ---")

            if self._send_command(zpl):
                print("  Etiqueta RFID (ZPL) enviada a impresora")
                return True
        except Exception as e:
            print(f"  Error: {e}")

        return False

    # ==========================================
    # IMPRESIÓN RFID - ZPL MÍNIMO
    # ==========================================

    def print_rfid_label_raw(self, epc_hex: str, label_text: str = "", barcode_data: str = "") -> bool:
        """
        Imprime etiqueta RFID con ZPL mínimo: solo encode RFID + texto simple.
        Útil para depuración: si esto funciona, el RFID está bien configurado.
        """
        if not self.is_connected:
            print("  Error: No conectado a la impresora")
            return False

        epc_hex = normalize_epc(epc_hex)
        if epc_hex is None:
            return False

        print(f"  [ZPL Mínimo] Solo RFID encode + texto simple...")
        print(f"    EPC: {epc_hex}")

        try:
            epc_bytes = len(epc_hex) // 2  # 12 bytes
            zpl = (
                "^XA"                                               # Inicio formato
                f"^PW{LABEL_WIDTH_DOTS}"                            # Ancho: 640 dots (80mm)
                f"^LL{LABEL_HEIGHT_DOTS}"                           # Alto: 160 dots (20mm)
                "^MNY"                                              # Gap sensing
                # --- RFID ---
                "^RS8,0,0,0,0,0"                                    # RFID setup: adaptive antenna
                "^RR3"                                              # 3 reintentos
                f"^RFW,H,2,{epc_bytes}^FD{epc_hex}^FS"             # Write EPC
                # --- Texto mínimo ---
                "^FO16,40^A0N,30,25^FDRFID OK^FS"                  # Solo un texto
                "^PQ1"                                              # 1 copia
                "^XZ"                                               # Fin formato
            )

            print(f"\n  Script ZPL enviado:")
            print(f"  ---")
            print(f"  {zpl}")
            print(f"  ---")

            if self._send_command(zpl):
                print("  Etiqueta RFID mínima enviada a impresora")
                return True
        except Exception as e:
            print(f"  Error: {e}")

        return False

    # ==========================================
    # ETIQUETA DE PRUEBA (sin RFID)
    # ==========================================

    def print_test_label(self, text: str) -> bool:
        """
        Imprime etiqueta de prueba (sin RFID) con ZPL puro.
        Sirve para verificar que ZGL está bien configurado.
        """
        if not self.is_connected:
            print("  Error: No conectado a la impresora")
            return False

        print(f"  Imprimiendo etiqueta de prueba (ZPL): {text}")

        try:
            zpl = (
                "^XA"
                f"^PW{LABEL_WIDTH_DOTS}"                            # 640 dots (80mm)
                f"^LL{LABEL_HEIGHT_DOTS}"                           # 160 dots (20mm)
                "^MNY"                                              # Gap sensing
                f"^FO16,15^A0N,28,22^FD{text}^FS"                  # Texto principal
                "^FO16,55^A0N,18,16^FDConexion OK (ZPL/ZGL)^FS"    # Subtexto
                "^PQ1"
                "^XZ"
            )

            print(f"  Script ZPL generado:")
            print(f"  {zpl}")

            if self._send_command(zpl):
                print("  Etiqueta de prueba (ZPL) enviada")
                return True
        except Exception as e:
            print(f"  Error: {e}")

        return False

    # ==========================================
    # CALIBRACIÓN DE MEDIA
    # ==========================================

    def calibrate_media(self) -> bool:
        """
        Calibra el media (gap sensing) de la impresora.
        IMPORTANTE: Ejecutar tras cambiar de TGL a ZGL.
        ~JC = calibración automática de media en ZPL.
        """
        if not self.is_connected:
            print("  Error: No conectado a la impresora")
            return False

        try:
            print("  Enviando comandos de calibración...")

            # 1. Configurar tipo de media y dimensiones
            setup = (
                "^XA"
                "^MNY"                                          # Media tracking: gap sensing
                f"^PW{LABEL_WIDTH_DOTS}"                        # Ancho: 640 dots (80mm)
                f"^LL{LABEL_HEIGHT_DOTS}"                       # Alto: 160 dots (20mm)
                "^JUS"                                          # Guardar config actual
                "^XZ"
            )
            self._send_command(setup)
            print("    Dimensiones configuradas: 80mm x 20mm")

            # 2. Calibración automática de media (~JC)
            self._send_command("~JC")
            print("    Calibración de gap enviada (~JC)")
            print("    Espera a que la impresora termine de calibrar...")

            return True
        except Exception as e:
            print(f"  Error calibrando: {e}")
            return False

    # ==========================================
    # COMANDO RAW
    # ==========================================

    def send_raw_command(self, command: str) -> bool:
        """Envía un comando ZPL/raw sin procesar."""
        if not self.is_connected:
            print("  Error: No conectado a la impresora")
            return False
        return self._send_command(command)

    # ==========================================
    # DESCONEXIÓN
    # ==========================================

    def disconnect(self):
        """Desconecta de la impresora."""
        try:
            if self._connected:
                self._comm.Close()
                print("  Desconectado de la impresora")
        except Exception:
            pass
        self._connected = False
        self._connection_type = ""
        self._connection_info = ""

    def __del__(self):
        self.disconnect()
