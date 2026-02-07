# Impresión RFID con Printronix T820 — Contexto y Aprendizajes

## Objetivo

Imprimir etiquetas con tag RFID (escribir EPC personalizado) desde un programa C# usando el SDK oficial UniPRT de TSC/Printronix, reemplazando el flujo manual con BarTender.

---

## Hardware

| Componente | Detalle |
|---|---|
| **Impresora** | Printronix T820 (familia T800, fabricada por TSC bajo marca Printronix Auto ID) |
| **Serial** | P-408231 |
| **IP** | 192.168.3.38 |
| **Puerto TCP** | 9100 |
| **Lector RFID** | Impinj (impinj-15-4b-ed) — para verificación |
| **Etiqueta** | 80mm x 20mm con inlay RFID UHF |
| **EPC** | 96 bits = 24 caracteres hexadecimales |

## Software / SDK

| Componente | Detalle |
|---|---|
| **SDK** | UniPRT SDK V2.0.0.3 |
| **Formato** | NuGet package (`UniPRT.Sdk.2.0.0.3.nupkg`) — NO es un DLL suelto |
| **Framework** | .NET 8.0 Console App (C#) |
| **Ubicación SDK** | `TSC UniPRT SDK_V2\Local\UniPRT_SDK_C#\Windows_Linux_macOS\` |
| **Documentación** | `Documentation\html_en-US\` (Doxygen HTML) |
| **Ejemplos** | `Example\UtilSnippet_TSPL.cs`, `RfidMonitorRfidReportSnippet.cs` |

---

## Cronología del Problema

### 1. Identificación del SDK correcto (Feb 5, 2026)

- **Problema**: No se sabía qué SDK usar. Se intentó Python SDK (falló), C# con TSCLIB.dll (no funcionó).
- **Solución**: El SDK correcto es **UniPRT SDK V2** descargado de la web de TSC. Viene como paquete NuGet, no como DLL individual.
- **Aprendizaje**: Para impresoras Printronix (adquiridas por TSC), el SDK unificado es UniPRT. TSCLIB.dll es para modelos TSC legacy.

### 2. Modelo de impresora (Feb 5)

- **Problema**: Se pensaba que era T800, pero la pantalla mostraba "T820".
- **Solución**: T820 es parte de la familia T800. Mismo SDK.

### 3. Lenguaje de la impresora (Feb 5)

- **Problema**: La impresora estaba en modo **PGL/LP+** (lenguaje Printronix). Los comandos TSPL no funcionaban.
- **Solución**: Cambiar a modo **TGL** (TSPL) desde: `Settings > Application > Control > Language > TGL`
- **Aprendizaje**: El T820 soporta múltiples lenguajes (PGL, TGL/TSPL, ZPL). Para usar el SDK con LabelMaker.TSPL, DEBE estar en TGL.

### 4. Conexión exitosa (Feb 6)

- Ethernet (`TcpConnection`) y USB (`UsbConnection`) funcionan correctamente.
- USB usa `UsbConnection.AvaliableDevices()` (nota: typo en el SDK, "Avaliable" no "Available").
- Conexión TCP en puerto 9100 estándar.

### 5. Impresión de texto funciona (Feb 6)

- Enviar TSPL puro simple (SIZE, GAP, CLS, TEXT, PRINT) **funciona perfectamente**.
- Esto confirma que la conexión y el modo TGL son correctos.

### 6. RFID falla con "Invalid Data" — Intento 1: Comandos raw (Feb 6-7)

- **Intentos fallidos**:
  ```
  RFIDTAG EPC,96,"000000000000000000000001"
  RFIDENCODE EPC,0,96,"000000000000000000000001"
  ```
- Ambos producen **"Invalid Data"** en la pantalla LCD de la impresora.
- **Aprendizaje**: Estos comandos TSPL genéricos no son la sintaxis correcta para el T820 con firmware TGL.

### 7. RFID falla con "Invalid Data" — Intento 2: SDK LabelMaker completo (Feb 7)

- Se usó el API de alto nivel del SDK:
  ```csharp
  var label = new Label("RfidLabel");
  label.AddRawContent("SIZE 4,2");
  label.AddObject(new RfidWrite(RfidMemBlockEnum.EPC, epcHex));
  label.AddObject(new Text(new TextItem(50f, 30f, "texto")));
  label.AddObject(new Barcode1D(barcodeItem));
  string tspl = label.ToString();
  connection.Write(Encoding.ASCII.GetBytes(tspl));
  ```
- El comando RFID generado es correcto: `RFID WRITE 0,H,0,96,EPC,"000000000000000000000001"`
- **PERO** el `Label.ToString()` genera boilerplate que el T820 NO soporta:
  ```
  DPI = 300
  FONT$ = "1"
  FH = 8
  FV = 12
  TEXT 50,(30 - 1*FV),FONT$,0,1,1,"texto"
  ```
- **Causa**: Variables TSPL (`FONT$`, `FV`, `FH`) y expresiones aritméticas (`30 - 1*FV`) son extensiones del lenguaje que solo funcionan en algunos modelos TSC nativos. El firmware TGL del Printronix T820 no las interpreta.
- **Aprendizaje clave**: El SDK LabelMaker genera TSPL "extendido" incompatible con el T820.

### 8. Dimensiones incorrectas de etiqueta (Feb 7)

- Se estaba usando `SIZE 4,2` (4" x 2" = 101mm x 50mm).
- La etiqueta real es **80mm x 20mm**.
- **Impacto en RFID**: Dimensiones incorrectas pueden causar que la antena no se alinee con el chip RFID del inlay, resultando en fallo de encode.
- **Corrección**: `SIZE 80 mm,20 mm`

---

### 9. CAUSA RAÍZ: TGL NO soporta RFID (Feb 7, 2026)

- **Descubrimiento**: Revisando los manuales oficiales de programación de Printronix:
  - **TGL Programmer's Reference** (`_58781f-prm-tgl-th.pdf`): Lista completa de comandos. **CERO comandos RFID**. Solo soporta: AR, AX, AY, C, D, IB, LC, PC, PV, RB, RC, RV, SG, T, XB, XS, etc.
  - **ZGL Programmer's Reference** (`258782f_prgm_manual_zgl_th.pdf`): **SÍ tiene comandos RFID**: ^RF, ^RB, ^RS, ^RW, ^WT, ^HR, ^RU, ^RZ
  - **PGL Programmer's Reference** (IGP/PGL): **SÍ tiene comandos RFID**: RFWTAG, RFRTAG
  
- **Causa del "Invalid Data"**: TGL (TEC Graphic Language) es emulación de impresoras Toshiba TEC. NO es lo mismo que TSPL (TSC Printer Language). Los comandos RFID (`RFID WRITE`, `RFIDTAG`, `RFIDENCODE`) simplemente no existen en TGL — la impresora los rechaza como datos inválidos.
  
- **Confusión original**: Se asumió que TGL = TSPL porque ambos son de TSC, pero TGL emula TEC, no TSC nativo.

- **Solución**: Cambiar de **TGL** a **ZGL** (emulación ZPL de Zebra):
  - `Settings > Application > Control > Active IGP Emul > ZGL`
  - Usar comandos ZPL estándar con `^RF` para RFID

---

## Solución Final: ZPL en modo ZGL

### Enfoque: ZPL con ^RF para RFID

La impresora DEBE estar en modo **ZGL** (no TGL). ZGL emula ZPL de Zebra y soporta todos los comandos RFID.

```zpl
^XA                                    // Inicio formato ZPL
^PW640                                 // Ancho: 640 dots (80mm @ 203dpi)
^LL160                                 // Alto: 160 dots (20mm @ 203dpi)
^MNY                                   // Gap/mark tracking
^RS8                                   // RFID setup: adaptive antenna
^RFW,H^FD000000000000000000000001^FS  // RFID Write EPC en hex
^FO20,10^A0N,25,25^FDRFID TEST^FS    // Texto
^FO20,40^A0N,18,18^FDEPC: 000...001^FS  // EPC visible
^FO20,70^BCN,50,Y,N,N^FD7501234567890^FS  // Code128 barcode
^PQ1                                   // Imprimir 1 copia
^XZ                                    // Fin formato
```

### Comandos RFID ZPL clave

| Comando | Descripción |
|---|---|
| `^RFW,H,2,12` | Write EPC: hex, word 2 (después CRC+PC), 12 bytes (96 bits) |
| `^RFR,H` | Read RFID, formato Hex |
| `^RS8,0,0,0,0,0` | RFID Setup: adaptive antenna, EPC encode |
| `^RR3` | 3 reintentos si falla encode |
| `^RB` | Define EPC Data Structure |
| `~JC` | Calibración automática de media (detecta gaps) |

### SDK UniPRT

- Se usa `UniPRT.Sdk.Comm` para la conexión TCP/USB.
- **NO existe** `LabelMaker.ZPL` — solo `LabelMaker.TSPL` que no sirve en ZGL.
- Los comandos ZPL se construyen como strings raw.
- `UniPRT.Sdk.Monitor.RfidMonitor` puede usarse para verificar encode (mejora futura).

---

## Aprendizajes Clave

### SDK UniPRT

1. **No es un DLL**: Es un paquete NuGet (`UniPRT.Sdk.2.0.0.3.nupkg`). Se integra con `<PackageReference>` y un `nuget.config` apuntando al directorio local.
2. **Namespaces principales**:
   - `UniPRT.Sdk.Comm` — Conexiones (TCP, USB, Bluetooth, COM)
   - `UniPRT.Sdk.LabelMaker.TSPL` — Generador de etiquetas (Label, Text, Barcode1D, RfidWrite)
   - `UniPRT.Sdk.LabelMaker.Interfaces` — Interfaces y enums (RfidMemBlockEnum, BarcodeTypeEnum_1D, etc.)
   - `UniPRT.Sdk.Monitor` — Monitoreo RFID/ODV
   - `UniPRT.Sdk.Settings` — Configuración de impresora via JSON
3. **LabelMaker genera código incompatible**: `Label.ToString()` incluye variables TSPL (`FONT$`, `DPI`, `FV`) que no todos los firmwares soportan.
4. **RfidWrite es útil standalone**: `new RfidWrite(RfidMemBlockEnum.EPC, data).ToString()` genera el comando correcto sin boilerplate.
5. **Barcode1D requiere BarcodeType**: Si no se establece `barcode.BarcodeType = BarcodeTypeEnum_1D.Code_128`, crashea con NullReferenceException en `ToString()`.
6. **Typo en API**: `AvaliableDevices()` (debería ser "Available") — así es en el SDK.

### Printronix T820

7. **TGL NO soporta RFID**: TGL (TEC Graphic Language) emula impresoras Toshiba TEC. NO es TSPL. No tiene ningún comando RFID — de ahí el "Invalid Data" persistente.
8. **ZGL SÍ soporta RFID**: ZGL (emulación ZPL/Zebra) tiene comandos RFID completos: ^RF, ^RB, ^RS, ^RW, ^WT.
9. **PGL también soporta RFID**: PGL (Printronix nativo) tiene RFWTAG y RFRTAG para RFID.
10. **Emulaciones disponibles**: PGL (Printronix nativo), ZGL (Zebra ZPL), TGL (Toshiba TEC). Para RFID usar ZGL o PGL.
11. **TGL acepta algo de TSPL**: Algunos comandos TSPL básicos (SIZE, GAP, TEXT, PRINT) funcionan en TGL, pero NO los de RFID.
12. **ZPL RFID syntax**: `^RFW,H^FD{hexdata}^FS` para escribir EPC. `^RS8` para setup de antena adaptiva.

### Dimensiones de Etiqueta

13. **Dimensiones afectan RFID**: Si las dimensiones no coinciden con el media físico, la antena no se alinea con el chip y el encode puede fallar.
14. **ZPL usa dots**: A 203 dpi: 80mm ≈ 640 dots, 20mm ≈ 160 dots. Se configura con `^PW640^LL160`.

### Inspección del SDK

13. **Reflexión .NET para explorar DLLs**: Se usó un proyecto auxiliar (`SdkInspector`) para inspeccionar constructores, propiedades y enums del SDK sin documentación clara.
14. **PowerShell 5.1 no carga .NET 8**: Para inspeccionar assemblies .NET 8, se debe usar un proyecto `dotnet run`, no PowerShell directo.

---

## Estructura del Proyecto

```
tag-print/
├── RfidTagPrinter/
│   ├── RfidTagPrinter.csproj     # net8.0, ref UniPRT.Sdk 2.0.0.3
│   ├── nuget.config               # Fuente NuGet local
│   ├── Program.cs                  # Menú consola con 9 opciones
│   ├── RfidPrinterService.cs      # Servicio principal (conexión + impresión)
│   └── UniPRT.Sdk.2.0.0.3.nupkg   # SDK empaquetado
├── SdkInspector/                   # Proyecto auxiliar para inspección por reflexión
├── TSC UniPRT SDK_V2/              # SDK completo con docs y ejemplos
├── PLAN_CONFIGURACION.md           # Pasos de configuración de impresora
├── README.md                       # Guía rápida
└── .gitignore
```

## Opciones del Menú Actual

| Opción | Descripción |
|---|---|
| 1 | Conectar por Ethernet (TCP/IP) |
| 2 | Conectar por USB |
| 3 | Ver estado de impresora |
| 4 | Imprimir etiqueta de prueba ZPL (sin RFID) |
| 5 | **RFID ZPL Completo** — ^RF + texto + barcode |
| 6 | **RFID ZPL Mínimo** — Solo ^RF encode (para depuración) |
| 7 | RFID con EPC personalizado |
| 8 | Desconectar |
| 9 | Enviar comando ZPL manual |
| 0 | Salir |

---

## Pendientes

- [ ] **Cambiar impresora a modo ZGL**: Settings > Application > Control > Active IGP Emul > ZGL
- [ ] Probar opción 4 (etiqueta ZPL sin RFID) para confirmar que ZGL funciona
- [ ] Probar opción 6 (RFID mínimo) para confirmar escritura de EPC
- [ ] Probar opción 5 (RFID completo con texto + barcode)
- [ ] Verificar EPC escrito con lector Impinj
- [ ] Ajustar posición de antena RFID si encode falla (`^RS` y `^HR` para calibración)
- [ ] Evaluar si se necesita `^RR` para reintentos de encode
- [ ] Integrar con sistema de producción (lectura de datos desde DB/API)
