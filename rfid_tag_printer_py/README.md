# RFID Tag Printer — Python / WSL

Versión Python del programa de impresión de etiquetas RFID para la Printronix T820, diseñada para ejecutarse en **WSL (Windows Subsystem for Linux)**.

Replica la funcionalidad de la versión C# (`RfidTagPrinter/`) usando el SDK UniPRT Python para Linux.

## Requisitos

- **WSL** (Ubuntu 22.04+ recomendado)
- **Python 3.8** (el SDK fue compilado con Python 3.8.10 — NO funciona con 3.9+)
- **Impresora Printronix T820** en modo **ZGL** (ZPL emulation)
  - `Settings > Application > Control > Active IGP Emul > ZGL`
- **Conectividad de red** entre WSL y la impresora (TCP/IP)

## Setup

### 1. Configurar el SDK (instala Python 3.8 + copia librerías)

```bash
cd rfid_tag_printer_py
chmod +x setup_sdk.sh
./setup_sdk.sh
```

El script hace todo automáticamente:
- Instala Python 3.8 desde deadsnakes PPA (si no existe)
- Instala libusb
- Copia las `.so` del SDK al directorio local `sdk_libs/`
- Verifica que la importación funcione

### 2. Ejecutar

```bash
python3.8 main.py
```

**IMPORTANTE:** Usar `python3.8`, NO `python3` (que probablemente es 3.12+).

## Estructura

```
rfid_tag_printer_py/
├── main.py                  # Programa principal (menú interactivo)
├── rfid_printer_service.py  # Servicio de impresión RFID (conexión + ZPL)
├── epc_encoder.py           # Codificador/decodificador EPC Empacor
├── setup_sdk.sh             # Script de setup para WSL
├── README.md                # Este archivo
└── sdk_libs/                # (generado por setup_sdk.sh) Librerías .so del SDK
```

## Funcionalidades

| Opción | Descripción |
|--------|-------------|
| 1 | Conectar por Ethernet (TCP/IP) |
| 2 | Conectar por USB (requiere usbipd en WSL) |
| 3 | Calibrar media (gap sensing) |
| 4 | Imprimir etiqueta de prueba ZPL (sin RFID) |
| 5 | Imprimir RFID ZPL completo (texto + barcode + RFID) |
| 6 | Imprimir RFID ZPL mínimo (solo encode, para depuración) |
| 7 | Imprimir RFID con EPC personalizado |
| 8 | Codificar código de despacho Empacor → EPC hex |
| 9 | Desconectar |
| m | Enviar comando ZPL manual |
| d | Decodificar EPC hex → código de despacho |
| 0 | Salir |

## Codificación EPC Empacor

El programa incluye un codificador/decodificador para el esquema EPC de Empacor:

```
PVE-219836-WAR-3270806  →  EAAA000219836BB003270806
```

Ver `EPC_ENCODING.md` en la raíz del proyecto para la especificación completa.

## Notas sobre WSL

### Red
WSL 2 generalmente tiene acceso a la red local. Si la impresora está en `192.168.3.38`, debería ser accesible desde WSL. Para verificar:

```bash
ping 192.168.3.38
```

Si no hay conectividad, puede ser necesario configurar WSL en modo "mirrored":

```powershell
# En PowerShell (Windows), crear/editar %USERPROFILE%\.wslconfig
[wsl2]
networkingMode=mirrored
```

### USB (opcional)
Para usar USB desde WSL se necesita [usbipd-win](https://github.com/dorssel/usbipd-win):

```powershell
# En PowerShell (Windows, admin)
winget install usbipd

# Listar dispositivos USB
usbipd list

# Pasar impresora a WSL
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

Para la mayoría de casos, **se recomienda usar la conexión Ethernet** (opción 1) que es más simple y confiable.

## Comparación con versión C#

| Aspecto | C# (RfidTagPrinter/) | Python (rfid_tag_printer_py/) |
|---------|----------------------|-------------------------------|
| Framework | .NET 8.0 | Python 3.10+ |
| SDK | UniPRT.Sdk NuGet | UniPRT SDK .so (Linux) |
| Plataforma | Windows | WSL (Linux) |
| Conexión | TCP/USB | TCP/USB |
| RFID | ZPL ^RF commands | ZPL ^RF commands (idéntico) |
| Extra | — | Codificador EPC Empacor integrado |

Los comandos ZPL enviados a la impresora son **idénticos** en ambas versiones.
