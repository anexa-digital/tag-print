using System;
using System.Reflection;

var asm = Assembly.LoadFrom(@"c:\Users\gerar\dev\empacor\RFID\tag-print\RfidTagPrinter\bin\Debug\net8.0\LabelMaker.dll");
var enumType = asm.GetType("UniPRT.Sdk.LabelMaker.Interfaces.BarcodeTypeEnum_1D");
if (enumType != null)
{
    Console.WriteLine("=== BarcodeTypeEnum_1D values ===");
    foreach (var v in Enum.GetValues(enumType))
        Console.WriteLine($"  {v} = {(int)v}");
}
