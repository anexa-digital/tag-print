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

## Solución Final (en pruebas)

### Enfoque Híbrido

Usar el SDK **solo para generar el comando RFID** (`RfidWrite.ToString()`), y construir el resto del TSPL de forma limpia (sin variables, sin boilerplate):

```csharp
// Solo el comando RFID viene del SDK
var rfidWrite = new RfidWrite(RfidMemBlockEnum.EPC, epcHex);
string rfidCommand = rfidWrite.ToString();
// Genera: RFID WRITE 0,H,0,96,EPC,"000000000000000000000001"

// El resto es TSPL limpio
var sb = new StringBuilder();
sb.AppendLine("SIZE 80 mm,20 mm");
sb.AppendLine("GAP 3 mm,0");
sb.AppendLine("DIRECTION 1");
sb.AppendLine("CLS");
sb.Append(rfidCommand);
sb.AppendLine("TEXT 30,10,\"2\",0,1,1,\"RFID TEST\"");
sb.AppendLine("TEXT 30,45,\"1\",0,1,1,\"EPC: 000...001\"");
sb.AppendLine("BARCODE 30,70,\"128\",40,1,0,2,2,\"7501234567890\"");
sb.AppendLine("PRINT 1,1");

connection.Write(Encoding.ASCII.GetBytes(sb.ToString()));
```

### Alternativa: TSPL 100% Puro

Sin depender del SDK para nada, usando la sintaxis `RFID WRITE` descubierta:

```
RFID WRITE 0,H,0,96,EPC,"000000000000000000000001"
```

Parámetros: `retry=0, format=H(hex), offset=0, bits=96, bank=EPC, data="..."`

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

7. **Modo TGL obligatorio**: Sin cambiar de PGL/LP+ a TGL, ningún comando TSPL funciona.
8. **No soporta TSPL extendido**: Variables (`DPI=300`, `FONT$="1"`) y expresiones aritméticas en parámetros (`30 - 1*FV`) causan "Invalid Data".
9. **TSPL puro funciona**: Comandos TSPL estándar (SIZE, GAP, CLS, TEXT, BARCODE, PRINT) funcionan perfecto.
10. **Sintaxis RFID correcta**: `RFID WRITE retry,format,offset,bits,bank,"data"` (descubierta del output del SDK).

### Dimensiones de Etiqueta

11. **SIZE afecta RFID**: Si las dimensiones no coinciden con el media físico, la antena no se alinea con el chip y el encode puede fallar.
12. **Formato SIZE con mm**: Se puede usar `SIZE 80 mm,20 mm` en lugar de pulgadas `SIZE 4,2`.

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
| 4 | Imprimir etiqueta de prueba (sin RFID) |
| 5 | **RFID Híbrido** — SDK RfidWrite + TSPL limpio |
| 6 | **RFID TSPL Puro** — Sin SDK, comando RFID WRITE directo |
| 7 | RFID con EPC personalizado |
| 8 | Desconectar |
| 9 | Enviar comando TSPL manual |
| 0 | Salir |

---

## Pendientes

- [ ] Confirmar que opción 6 (TSPL puro) o 5 (híbrido) escriben el EPC correctamente
- [ ] Verificar EPC escrito con lector Impinj
- [ ] Ajustar GAP si las etiquetas no se posicionan bien (actualmente 3mm)
- [ ] Evaluar si se necesita `RFIDRETRY` para reintentos de encode
- [ ] Integrar con sistema de producción (lectura de datos desde DB/API)
