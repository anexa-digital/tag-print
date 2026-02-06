namespace RfidTagPrinter;

/// <summary>
/// Programa de prueba para impresión RFID en Printronix T820
/// Usando SDK oficial UniPRT de TSC
/// 
/// ANTES DE EJECUTAR:
/// 1. Cambiar lenguaje de impresora a TSPL (ver PLAN_CONFIGURACION.md)
/// 2. Verificar IP de la impresora (actual: 192.168.3.38)
/// </summary>
class Program
{
    // ============================================
    // CONFIGURACIÓN - MODIFICAR SEGÚN TU ENTORNO
    // ============================================
    
    /// <summary>
    /// IP de la impresora Printronix T820
    /// </summary>
    const string PRINTER_IP = "192.168.3.38";
    
    /// <summary>
    /// Puerto TCP (estándar: 9100)
    /// </summary>
    const int PRINTER_PORT = 9100;

    // ============================================
    // DATOS DE PRUEBA HARDCODEADOS
    // ============================================
    
    /// <summary>
    /// EPC de prueba (96 bits = 24 caracteres hexadecimales)
    /// Usando valores simples para facilitar depuración
    /// </summary>
    const string TEST_EPC = "000000000000000000000001";
    
    /// <summary>
    /// Texto visible en la etiqueta
    /// </summary>
    const string TEST_LABEL_TEXT = "RFID TEST - EMPACOR";
    
    /// <summary>
    /// Código de barras en la etiqueta
    /// </summary>
    const string TEST_BARCODE = "7501234567890";

    static RfidPrinterService? _printer;

    static void Main(string[] args)
    {
        Console.WriteLine("═══════════════════════════════════════════════════════════");
        Console.WriteLine("     RFID Tag Printer - Printronix T820                    ");
        Console.WriteLine("     SDK: UniPRT 2.0                                       ");
        Console.WriteLine("═══════════════════════════════════════════════════════════");
        Console.WriteLine();

        // Mostrar menú
        bool running = true;
        while (running)
        {
            Console.WriteLine();
            Console.WriteLine("Opciones:");
            Console.WriteLine("  1. Conectar por Ethernet (TCP/IP)");
            Console.WriteLine("  2. Conectar por USB");
            Console.WriteLine("  3. Ver estado de impresora");
            Console.WriteLine("  4. Imprimir etiqueta de prueba (sin RFID)");
            Console.WriteLine("  5. Imprimir etiqueta RFID (formato RFIDTAG)");
            Console.WriteLine("  6. Imprimir etiqueta RFID con EPC personalizado");
            Console.WriteLine("  7. Desconectar");
            Console.WriteLine("  8. Probar comando RFID alternativo (RFIDENCODE)");
            Console.WriteLine("  9. Enviar comando TSPL manual");
            Console.WriteLine("  0. Salir");
            Console.WriteLine();
            Console.Write("Seleccione opción: ");

            var key = Console.ReadKey();
            Console.WriteLine();
            Console.WriteLine();

            switch (key.KeyChar)
            {
                case '1':
                    ConnectEthernet();
                    break;

                case '2':
                    ConnectUsb();
                    break;

                case '3':
                    ShowPrinterStatus();
                    break;

                case '4':
                    PrintSimpleTest();
                    break;

                case '5':
                    PrintRfidTest();
                    break;

                case '6':
                    PrintRfidCustom();
                    break;

                case '7':
                    DisconnectPrinter();
                    break;

                case '8':
                    PrintRfidAlternative();
                    break;

                case '9':
                    SendManualCommand();
                    break;

                case '0':
                    running = false;
                    break;

                default:
                    Console.WriteLine("Opción no válida");
                    break;
            }
        }

        _printer?.Dispose();
        Console.WriteLine("👋 Programa terminado");
    }

    static void ConnectEthernet()
    {
        _printer?.Dispose();
        
        Console.Write($"📡 IP de la impresora [{PRINTER_IP}]: ");
        string? input = Console.ReadLine();
        string ip = string.IsNullOrWhiteSpace(input) ? PRINTER_IP : input;
        
        _printer = new RfidPrinterService(ip, PRINTER_PORT);
        
        if (_printer.Connect())
        {
            Console.WriteLine("✅ Conexión Ethernet exitosa!");
        }
        else
        {
            Console.WriteLine("❌ No se pudo conectar. Verifica:");
            Console.WriteLine("   - Que la impresora esté encendida y ONLINE");
            Console.WriteLine("   - Que el lenguaje esté en TSPL (no PGL/LP+)");
            Console.WriteLine($"   - Que la IP {ip} sea correcta");
            Console.WriteLine("   - Que el puerto 9100 esté abierto");
        }
    }

    static void ConnectUsb()
    {
        _printer?.Dispose();
        
        Console.WriteLine("🔌 Buscando impresoras USB...");
        var devices = RfidPrinterService.ListUsbDevices();

        if (devices.Count == 0)
        {
            Console.WriteLine("❌ No se encontraron impresoras USB");
            return;
        }

        for (int i = 0; i < devices.Count; i++)
        {
            Console.WriteLine($"   [{i}] {devices[i].description}");
        }

        Console.Write("Seleccione índice USB [0]: ");
        string? input = Console.ReadLine();
        int index = 0;
        if (!string.IsNullOrWhiteSpace(input) && int.TryParse(input, out int parsed))
        {
            index = parsed;
        }

        _printer = new RfidPrinterService(index);
        
        if (_printer.Connect())
        {
            Console.WriteLine("✅ Conexión USB exitosa!");
        }
        else
        {
            Console.WriteLine("❌ No se pudo conectar por USB. Verifica:");
            Console.WriteLine("   - Que la impresora esté conectada por USB");
            Console.WriteLine("   - Que la impresora esté encendida y ONLINE");
            Console.WriteLine("   - Que el lenguaje esté en TGL (TSPL)");
        }
    }

    static void DisconnectPrinter()
    {
        if (_printer != null)
        {
            _printer.Disconnect();
            _printer.Dispose();
            _printer = null;
        }
        else
        {
            Console.WriteLine("ℹ️ No hay conexión activa");
        }
    }

    static void ShowPrinterStatus()
    {
        if (_printer == null)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
        Console.WriteLine("📊 Consultando estado...");
        string status = _printer.GetStatus();
        Console.WriteLine($"   Estado: {status}");
    }

    static void PrintSimpleTest()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
        Console.WriteLine("🏷️ Imprimiendo etiqueta de prueba simple...");
        
        if (_printer.PrintTestLabel("TEST CONEXION"))
        {
            Console.WriteLine("✅ Etiqueta enviada. Verifica que se imprimió.");
        }
    }

    static void PrintRfidTest()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
        Console.WriteLine("🏷️ Imprimiendo etiqueta RFID de prueba...");
        Console.WriteLine($"   EPC: {TEST_EPC}");
        Console.WriteLine($"   Texto: {TEST_LABEL_TEXT}");
        Console.WriteLine($"   Código: {TEST_BARCODE}");
        Console.WriteLine();

        if (_printer.PrintRfidLabel(TEST_EPC, TEST_LABEL_TEXT, TEST_BARCODE))
        {
            Console.WriteLine();
            Console.WriteLine("✅ Etiqueta RFID enviada!");
            Console.WriteLine("   Verifica con un lector RFID que el EPC se escribió correctamente.");
        }
    }

    static void PrintRfidCustom()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
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

        if (_printer.PrintRfidLabel(epc, text, barcode))
        {
            Console.WriteLine("✅ Etiqueta RFID personalizada enviada!");
        }
    }

    static void PrintRfidAlternative()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
        Console.WriteLine("🏷️ Probando con formato RFIDENCODE alternativo...");
        Console.WriteLine($"   EPC: {TEST_EPC}");
        Console.WriteLine();

        if (_printer.PrintRfidLabelAlternative(TEST_EPC, TEST_LABEL_TEXT))
        {
            Console.WriteLine();
            Console.WriteLine("✅ Etiqueta enviada con formato alternativo!");
        }
    }

    static void SendManualCommand()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
        Console.WriteLine("📝 Ingrese el comando TSPL (o 'test' para un comando de prueba):");
        Console.Write("> ");
        string command = Console.ReadLine() ?? "";

        if (command.ToLower() == "test")
        {
            command = "SIZE 4,2\nGAP 0.12,0\nCLS\nTEXT 50,50,\"3\",0,1,1,\"TEST MANUAL\"\nPRINT 1,1\n";
            Console.WriteLine($"Enviando comando de prueba:");
            Console.WriteLine(command);
        }

        if (!string.IsNullOrWhiteSpace(command))
        {
            if (_printer.SendRawCommand(command))
            {
                Console.WriteLine("✅ Comando enviado!");
            }
        }
    }
}
