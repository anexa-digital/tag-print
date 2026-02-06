# RFID Tag Printer - Printronix T820

Programa de prueba para imprimir etiquetas RFID con la impresora Printronix T820.
**Usa SDK oficial UniPRT 2.0 de TSC.**

## Requisitos Previos

### 1. Cambiar Lenguaje de Impresora a TSPL
La impresora debe estar en modo **TSPL** (no PGL/LP+):
1. En el panel LCD ir a **Settings**
2. Buscar **Emulation** o **Printer Language**
3. Cambiar a **TSPL** o **ZPL2**
4. Guardar y reiniciar

### 2. Verificar Configuración de Red
```
IP Impresora: 192.168.3.60
Puerto: 9100
```

## Compilar y Ejecutar

```bash
cd RfidTagPrinter
dotnet restore
dotnet build
dotnet run
```

## Estructura del Proyecto

```
RfidTagPrinter/
├── Program.cs              # Menú principal de prueba
├── RfidPrinterService.cs   # Lógica de impresión RFID (usa UniPRT SDK)
├── RfidTagPrinter.csproj   # Configuración del proyecto
├── nuget.config            # Fuente local del SDK
└── UniPRT.Sdk.2.0.0.3.nupkg # SDK de TSC (paquete NuGet local)
```

## Uso

1. Ejecutar el programa
2. Opción 1: Conectar a impresora
3. Opción 2: Ver estado (verificar que está ONLINE)
4. Opción 3: Imprimir etiqueta simple (prueba de conexión)
5. Opción 4: Imprimir etiqueta RFID con EPC de prueba

## EPC de Prueba

```
E20034120123456789ABCDEF
```
(96 bits = 24 caracteres hexadecimales)

## Troubleshooting

| Problema | Solución |
|----------|----------|
| DLL no encontrada | Copiar TSCLIB.dll a la carpeta del proyecto |
| No conecta | Verificar IP y que impresora esté en modo TSPL |
| RFID no escribe | Verificar que la etiqueta tenga chip RFID |
