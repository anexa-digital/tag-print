namespace RfidTagPrinter;

/// <summary>
/// Programa de prueba para impresión RFID en Printronix T820
/// Usando SDK oficial UniPRT de TSC
/// 
/// ANTES DE EJECUTAR:
/// 1. Cambiar lenguaje de impresora a TSPL (ver PLAN_CONFIGURACION.md)
/// 2. Verificar IP de la impresora (actual: 192.168.3.60)
/// </summary>
class Program
{
    // ============================================
    // CONFIGURACIÓN - MODIFICAR SEGÚN TU ENTORNO
    // ============================================
    
    /// <summary>
    /// IP de la impresora Printronix T820
    /// </summary>
    const string PRINTER_IP = "192.168.3.60";
    
    /// <summary>
    /// Puerto TCP (estándar: 9100)
    /// </summary>
    const int PRINTER_PORT = 9100;

    // ============================================
    // DATOS DE PRUEBA HARDCODEADOS
    // ============================================
    
    /// <summary>
    /// EPC de prueba (96 bits = 24 caracteres hexadecimales)
    /// </summary>
    const string TEST_EPC = "E20034120123456789ABCDEF";
    
    /// <summary>
    /// Texto visible en la etiqueta
    /// </summary>
    const string TEST_LABEL_TEXT = "RFID TEST - EMPACOR";
    
    /// <summary>
    /// Código de barras en la etiqueta
    /// </summary>
    const string TEST_BARCODE = "7501234567890";

    static void Main(string[] args)
    {
        Console.WriteLine("═══════════════════════════════════════════════════════════");
        Console.WriteLine("     RFID Tag Printer - Printronix T820                    ");
        Console.WriteLine("     SDK: UniPRT 2.0                                       ");
        Console.WriteLine("═══════════════════════════════════════════════════════════");
        Console.WriteLine();

        // Crear servicio de impresión (solo TCP/IP con el nuevo SDK)
        using var printer = new RfidPrinterService(PRINTER_IP, PRINTER_PORT);

        // Mostrar menú
        bool running = true;
        while (running)
        {
            Console.WriteLine();
            Console.WriteLine("Opciones:");
            Console.WriteLine("  1. Conectar a impresora");
            Console.WriteLine("  2. Ver estado de impresora");
            Console.WriteLine("  3. Imprimir etiqueta de prueba (sin RFID)");
            Console.WriteLine("  4. Imprimir etiqueta RFID con EPC de prueba");
            Console.WriteLine("  5. Imprimir etiqueta RFID con EPC personalizado");
            Console.WriteLine("  0. Salir");
            Console.WriteLine();
            Console.Write("Seleccione opción: ");

            var key = Console.ReadKey();
            Console.WriteLine();
            Console.WriteLine();

            switch (key.KeyChar)
            {
                case '1':
                    ConnectPrinter(printer);
                    break;

                case '2':
                    ShowPrinterStatus(printer);
                    break;

                case '3':
                    PrintSimpleTest(printer);
                    break;

                case '4':
                    PrintRfidTest(printer);
                    break;

                case '5':
                    PrintRfidCustom(printer);
                    break;

                case '0':
                    running = false;
                    break;

                default:
                    Console.WriteLine("Opción no válida");
                    break;
            }
        }

        Console.WriteLine("👋 Programa terminado");
    }

    static void ConnectPrinter(RfidPrinterService printer)
    {
        Console.WriteLine("🔄 Intentando conectar...");
        
        if (printer.Connect())
        {
            Console.WriteLine("✅ Conexión exitosa!");
        }
        else
        {
            Console.WriteLine("❌ No se pudo conectar. Verifica:");
            Console.WriteLine("   - Que la impresora esté encendida y ONLINE");
            Console.WriteLine("   - Que el lenguaje esté en TSPL (no PGL/LP+)");
            Console.WriteLine($"   - Que la IP {PRINTER_IP} sea correcta");
            Console.WriteLine("   - Que el puerto 9100 esté abierto");
        }
    }

    static void ShowPrinterStatus(RfidPrinterService printer)
    {
        Console.WriteLine("📊 Consultando estado...");
        
        string status = printer.GetStatus();
        Console.WriteLine($"   Estado: {status}");
    }

    static void PrintSimpleTest(RfidPrinterService printer)
    {
        Console.WriteLine("🏷️ Imprimiendo etiqueta de prueba simple...");
        
        if (printer.PrintTestLabel("TEST CONEXION"))
        {
            Console.WriteLine("✅ Etiqueta enviada. Verifica que se imprimió.");
        }
    }

    static void PrintRfidTest(RfidPrinterService printer)
    {
        Console.WriteLine("🏷️ Imprimiendo etiqueta RFID de prueba...");
        Console.WriteLine($"   EPC: {TEST_EPC}");
        Console.WriteLine($"   Texto: {TEST_LABEL_TEXT}");
        Console.WriteLine($"   Código: {TEST_BARCODE}");
        Console.WriteLine();

        if (printer.PrintRfidLabel(TEST_EPC, TEST_LABEL_TEXT, TEST_BARCODE))
        {
            Console.WriteLine();
            Console.WriteLine("✅ Etiqueta RFID enviada!");
            Console.WriteLine("   Verifica con un lector RFID que el EPC se escribió correctamente.");
        }
    }

    static void PrintRfidCustom(RfidPrinterService printer)
    {
        Console.WriteLine("📝 Ingresa los datos para la etiqueta RFID:");
        Console.WriteLine();

        Console.Write("   EPC (24 caracteres hex, ej: E20034120123456789ABCDEF): ");
        string epc = Console.ReadLine() ?? TEST_EPC;
        
        if (string.IsNullOrWhiteSpace(epc))
            epc = TEST_EPC;

        Console.Write("   Texto de etiqueta: ");
        string text = Console.ReadLine() ?? "CUSTOM RFID";
        
        if (string.IsNullOrWhiteSpace(text))
            text = "CUSTOM RFID";

        Console.Write("   Código de barras: ");
        string barcode = Console.ReadLine() ?? "123456789";
        
        if (string.IsNullOrWhiteSpace(barcode))
            barcode = "123456789";

        Console.WriteLine();
        Console.WriteLine($"   Imprimiendo con EPC: {epc}");

        if (printer.PrintRfidLabel(epc, text, barcode))
        {
            Console.WriteLine("✅ Etiqueta RFID personalizada enviada!");
        }
    }
}
