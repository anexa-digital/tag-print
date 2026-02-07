"""
Codificador/Decodificador EPC para Empacor RFID

Esquema para codificar códigos de despacho tipo "PVE-219836-WAR-3270806"
en los 96 bits (12 bytes = 24 caracteres hex) del EPC de un tag RFID UHF.

Estructura (24 hex chars):
  Pos 0-1:   Formato/versión (EA = v1)
  Pos 2-3:   Prefijo tipo documento (AA=PVE, AB=PVZ, AC=PVI)
  Pos 4-12:  Número 1 (9 dígitos, zero-pad)
  Pos 13-14: Prefijo tipo ubicación (BA=DIR, BB=WAR, BC=DEV, BD=AJU)
  Pos 15-23: Número 2 (9 dígitos, zero-pad)

Ejemplo: PVE-219836-WAR-3270806 → EAAA000219836BB003270806
"""

import re
from typing import Optional, Tuple

# ============================================
# TABLAS DE MAPEO
# ============================================

# Formato/versión
FORMAT_VERSION = "EA"  # Empacor formato v1

# Prefijo 1 — Tipo de documento
DOC_TYPE_TO_HEX = {
    "PVE": "AA",
    "PVZ": "AB",
    "PVI": "AC",
}

HEX_TO_DOC_TYPE = {v: k for k, v in DOC_TYPE_TO_HEX.items()}

# Prefijo 2 — Tipo de ubicación
LOC_TYPE_TO_HEX = {
    "DIR": "BA",
    "WAR": "BB",
    "DEV": "BC",
    "AJU": "BD",
}

HEX_TO_LOC_TYPE = {v: k for k, v in LOC_TYPE_TO_HEX.items()}


# ============================================
# ENCODE: código → EPC hex
# ============================================

def encode_dispatch_code(code: str) -> Optional[str]:
    """
    Codifica un código de despacho a EPC hex de 24 caracteres.
    
    Entrada: "PVE-219836-WAR-3270806"
    Salida:  "EAAA000219836BB003270806"
    
    Retorna None si el formato es inválido.
    """
    code = code.strip().upper()
    
    # Parsear por guiones
    parts = code.split("-")
    if len(parts) != 4:
        print(f"  Error: Se esperan 4 partes separadas por guiones, se obtuvieron {len(parts)}")
        print(f"  Formato: TIPO_DOC-NUMERO1-TIPO_UBIC-NUMERO2")
        print(f"  Ejemplo: PVE-219836-WAR-3270806")
        return None
    
    doc_type, num1_str, loc_type, num2_str = parts
    
    # Validar tipo de documento
    if doc_type not in DOC_TYPE_TO_HEX:
        valid = ", ".join(DOC_TYPE_TO_HEX.keys())
        print(f"  Error: Tipo de documento '{doc_type}' no reconocido. Válidos: {valid}")
        return None
    
    # Validar tipo de ubicación
    if loc_type not in LOC_TYPE_TO_HEX:
        valid = ", ".join(LOC_TYPE_TO_HEX.keys())
        print(f"  Error: Tipo de ubicación '{loc_type}' no reconocido. Válidos: {valid}")
        return None
    
    # Validar números
    if not num1_str.isdigit():
        print(f"  Error: Número 1 '{num1_str}' no es numérico")
        return None
    if not num2_str.isdigit():
        print(f"  Error: Número 2 '{num2_str}' no es numérico")
        return None
    
    num1 = int(num1_str)
    num2 = int(num2_str)
    
    if num1 > 999_999_999:
        print(f"  Error: Número 1 ({num1}) excede máximo (999999999)")
        return None
    if num2 > 999_999_999:
        print(f"  Error: Número 2 ({num2}) excede máximo (999999999)")
        return None
    
    # Construir EPC
    epc = (
        FORMAT_VERSION
        + DOC_TYPE_TO_HEX[doc_type]
        + f"{num1:09d}"
        + LOC_TYPE_TO_HEX[loc_type]
        + f"{num2:09d}"
    )
    
    assert len(epc) == 24, f"EPC debería tener 24 chars, tiene {len(epc)}"
    return epc


# ============================================
# DECODE: EPC hex → código
# ============================================

def decode_epc(epc_hex: str) -> Optional[str]:
    """
    Decodifica un EPC hex de 24 caracteres a código de despacho.
    
    Entrada: "EAAA000219836BB003270806"
    Salida:  "PVE-219836-WAR-3270806"
    
    Retorna None si el formato no es reconocido.
    """
    epc_hex = epc_hex.strip().upper()
    
    if len(epc_hex) != 24:
        print(f"  Error: EPC debe tener 24 caracteres hex, tiene {len(epc_hex)}")
        return None
    
    # Validar que inicia con 'E' (tag Empacor)
    if not epc_hex.startswith("E"):
        print(f"  Error: EPC no inicia con 'E' — no es un tag Empacor")
        return None
    
    # Leer formato/versión
    version = epc_hex[0:2]
    if version != FORMAT_VERSION:
        print(f"  Advertencia: Versión de formato '{version}' (esperado '{FORMAT_VERSION}')")
    
    # Leer prefijo 1
    prefix1_hex = epc_hex[2:4]
    if prefix1_hex not in HEX_TO_DOC_TYPE:
        print(f"  Error: Prefijo de documento '{prefix1_hex}' no reconocido")
        return None
    doc_type = HEX_TO_DOC_TYPE[prefix1_hex]
    
    # Leer número 1
    num1_str = epc_hex[4:13]
    if not num1_str.isdigit():
        print(f"  Error: Número 1 '{num1_str}' no es numérico")
        return None
    num1 = str(int(num1_str))  # Eliminar ceros iniciales
    
    # Leer prefijo 2
    prefix2_hex = epc_hex[13:15]
    if prefix2_hex not in HEX_TO_LOC_TYPE:
        print(f"  Error: Prefijo de ubicación '{prefix2_hex}' no reconocido")
        return None
    loc_type = HEX_TO_LOC_TYPE[prefix2_hex]
    
    # Leer número 2
    num2_str = epc_hex[15:24]
    if not num2_str.isdigit():
        print(f"  Error: Número 2 '{num2_str}' no es numérico")
        return None
    num2 = str(int(num2_str))  # Eliminar ceros iniciales
    
    return f"{doc_type}-{num1}-{loc_type}-{num2}"


# ============================================
# VALIDACIÓN DE EPC HEX
# ============================================

def normalize_epc(epc_hex: str) -> Optional[str]:
    """
    Normaliza y valida un EPC hexadecimal a exactamente 24 caracteres.
    - Convierte a mayúsculas
    - Elimina espacios
    - Valida caracteres hex
    - Rellena/trunca a 24 caracteres
    
    Retorna None si contiene caracteres no hexadecimales.
    """
    epc_hex = epc_hex.upper().replace(" ", "")
    
    if not re.match(r'^[0-9A-F]+$', epc_hex):
        print("  Error: EPC contiene caracteres no hexadecimales")
        return None
    
    if len(epc_hex) < 24:
        epc_hex = epc_hex.ljust(24, '0')
        print(f"  Advertencia: EPC rellenado a 24 chars: {epc_hex}")
    elif len(epc_hex) > 24:
        epc_hex = epc_hex[:24]
        print(f"  Advertencia: EPC truncado a 24 chars: {epc_hex}")
    
    return epc_hex


# ============================================
# DEMO / TEST
# ============================================

if __name__ == "__main__":
    print("=== Test EPC Encoder ===\n")
    
    test_cases = [
        "PVE-219836-WAR-3270806",
        "PVZ-001234-DIR-0000001",
        "PVI-999999-DEV-9999999",
        "PVE-100000-AJU-5555555",
    ]
    
    for code in test_cases:
        epc = encode_dispatch_code(code)
        if epc:
            decoded = decode_epc(epc)
            status = "OK" if decoded == code else f"MISMATCH: {decoded}"
            print(f"  {code:30s} -> {epc} -> {status}")
        else:
            print(f"  {code:30s} -> ERROR")
    
    print("\n=== Test Normalize EPC ===\n")
    print(f"  Short:  {normalize_epc('ABCD')}")
    print(f"  Long:   {normalize_epc('EAAA000219836BB003270806FF')}")
    print(f"  Normal: {normalize_epc('EAAA000219836BB003270806')}")
