using System;
using System.Reflection;
using System.Linq;

var asm = Assembly.LoadFrom(@"c:\Users\gerar\dev\empacor\RFID\tag-print\RfidTagPrinter\bin\Debug\net8.0\LabelMaker.dll");

// Check RfidWrite.ToString() standalone
var rfidType = asm.GetType("UniPRT.Sdk.LabelMaker.TSPL.RfidWrite");
var enumType = asm.GetType("UniPRT.Sdk.LabelMaker.Interfaces.RfidMemBlockEnum");
if (rfidType != null && enumType != null)
{
    var epcValue = Enum.Parse(enumType, "EPC");
    var rfid = Activator.CreateInstance(rfidType, epcValue, "000000000000000000000001");
    var result = rfid?.ToString();
    Console.WriteLine("=== RfidWrite.ToString() standalone ===");
    Console.WriteLine($"[{result}]");
    Console.WriteLine("=== END ===");
}

// Check Barcode1D properties and defaults
var barcodeEnumType = asm.GetType("UniPRT.Sdk.LabelMaker.Interfaces.BarcodeTypeEnum_1D");
if (barcodeEnumType != null)
{
    Console.WriteLine("\n=== BarcodeTypeEnum_1D values ===");
    foreach (var v in Enum.GetValues(barcodeEnumType))
        Console.WriteLine($"  {v} = {(int)v}");
}

// Check if BarWidths has defaults
var barWidthsType = asm.GetType("UniPRT.Sdk.LabelMaker.TSPL.BarWidths");
if (barWidthsType != null)
{
    Console.WriteLine("\n=== BarWidths Constructors ===");
    foreach (var c in barWidthsType.GetConstructors())
    {
        var ps = string.Join(", ", c.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
        Console.WriteLine($"  Ctor({ps})");
    }
    Console.WriteLine("=== BarWidths Properties ===");
    foreach (var p in barWidthsType.GetProperties())
        Console.WriteLine($"  {p.PropertyType.Name} {p.Name}");
}
