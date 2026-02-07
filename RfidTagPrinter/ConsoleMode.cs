namespace RfidTagPrinter;

/// <summary>
/// Modo interactivo de consola para impresión RFID en Printronix T820.
/// Usar con: dotnet run -- --console
/// </summary>
public static class ConsoleMode
{
    // Configuración por defecto
    private const string PRINTER_IP = "192.168.3.38";
    private const int PRINTER_PORT = 9100;

    // Datos de prueba
    private const string TEST_EPC = "000000000000000000000001";
    private const string TEST_LABEL_TEXT = "RFID TEST - EMPACOR";
    private const string TEST_BARCODE = "7501234567890";

    private static RfidPrinterService? _printer;

    public static void Run(string[] args)
    {
        Console.WriteLine("═══════════════════════════════════════════════════════════");
        Console.WriteLine("     RFID Tag Printer - Printronix T820                    ");
        Console.WriteLine("     Modo: ZGL (ZPL) + UniPRT SDK (conexión)              ");
        Console.WriteLine("═══════════════════════════════════════════════════════════");
        Console.WriteLine();

        bool running = true;
        while (running)
        {
            Console.WriteLine();
            Console.WriteLine("Opciones:");
            Console.WriteLine("  1. Conectar por Ethernet (TCP/IP)");
            Console.WriteLine("  2. Conectar por USB");
            Console.WriteLine("  3. Calibrar media (IMPORTANTE tras cambiar a ZGL)");
            Console.WriteLine("  4. Imprimir etiqueta de prueba ZPL (sin RFID)");
            Console.WriteLine("  5. Imprimir etiqueta RFID - ZPL completo (texto+barcode+RFID)");
            Console.WriteLine("  6. Imprimir etiqueta RFID - ZPL mínimo (solo RFID encode)");
            Console.WriteLine("  7. Imprimir etiqueta RFID con EPC personalizado");
            Console.WriteLine("  8. Desconectar");
            Console.WriteLine("  9. Enviar comando ZPL manual");
            Console.WriteLine("  0. Salir");
            Console.WriteLine();
            Console.Write("Seleccione opción: ");

            var key = Console.ReadKey();
            Console.WriteLine();
            Console.WriteLine();

            switch (key.KeyChar)
            {
                case '1': ConnectEthernet(); break;
                case '2': ConnectUsb(); break;
                case '3': CalibrateMedia(); break;
                case '4': PrintSimpleTest(); break;
                case '5': PrintRfidTestHybrid(); break;
                case '6': PrintRfidTestRaw(); break;
                case '7': PrintRfidCustom(); break;
                case '8': DisconnectPrinter(); break;
                case '9': SendManualCommand(); break;
                case '0': running = false; break;
                default: Console.WriteLine("Opción no válida"); break;
            }
        }

        _printer?.Dispose();
        Console.WriteLine("👋 Programa terminado");
    }

    private static void ConnectEthernet()
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
            Console.WriteLine("   - Que el lenguaje esté en ZGL (no TGL ni PGL)");
            Console.WriteLine($"   - Que la IP {ip} sea correcta");
            Console.WriteLine("   - Que el puerto 9100 esté abierto");
        }
    }

    private static void ConnectUsb()
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
            Console.WriteLine($"   [{i}] {devices[i].description}");

        Console.Write("Seleccione índice USB [0]: ");
        string? input = Console.ReadLine();
        int index = 0;
        if (!string.IsNullOrWhiteSpace(input) && int.TryParse(input, out int parsed))
            index = parsed;

        _printer = new RfidPrinterService(index);

        if (_printer.Connect())
            Console.WriteLine("✅ Conexión USB exitosa!");
        else
        {
            Console.WriteLine("❌ No se pudo conectar por USB. Verifica:");
            Console.WriteLine("   - Que la impresora esté conectada por USB");
            Console.WriteLine("   - Que la impresora esté encendida y ONLINE");
            Console.WriteLine("   - Que el lenguaje esté en ZGL");
        }
    }

    private static void DisconnectPrinter()
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

    private static bool RequireConnection()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return false;
        }
        return true;
    }

    private static void CalibrateMedia()
    {
        if (!RequireConnection()) return;

        Console.WriteLine("📏 Calibrando media...");
        Console.WriteLine("   La impresora avanzará algunas etiquetas para detectar el gap.");
        Console.WriteLine("   Esto es NECESARIO tras cambiar de TGL a ZGL.");
        Console.WriteLine();

        var result = _printer!.CalibrateMedia();
        Console.WriteLine(result.Success ? $"✅ {result.Message}" : $"❌ {result.Message}");
    }

    private static void PrintSimpleTest()
    {
        if (!RequireConnection()) return;

        Console.WriteLine("🏷️ Imprimiendo etiqueta de prueba simple...");
        var result = _printer!.PrintTestLabel("TEST CONEXION");
        Console.WriteLine(result.Success ? $"✅ {result.Message}" : $"❌ {result.Message}");
    }

    private static void PrintRfidTestHybrid()
    {
        if (!RequireConnection()) return;

        Console.WriteLine("🏷️ [ZPL Completo] RFID + texto + barcode");
        Console.WriteLine($"   EPC: {TEST_EPC}");
        Console.WriteLine($"   Texto: {TEST_LABEL_TEXT}");
        Console.WriteLine($"   Código: {TEST_BARCODE}");
        Console.WriteLine();

        var result = _printer!.PrintRfidLabel(TEST_EPC, TEST_LABEL_TEXT, TEST_BARCODE);
        if (result.Success)
        {
            Console.WriteLine();
            Console.WriteLine("✅ Etiqueta RFID enviada!");
            Console.WriteLine("   Verifica con un lector RFID que el EPC se escribió correctamente.");
        }
        else
        {
            Console.WriteLine($"❌ {result.Message}");
        }
    }

    private static void PrintRfidTestRaw()
    {
        if (!RequireConnection()) return;

        Console.WriteLine("🏷️ [ZPL Mínimo] Solo RFID encode - para depuración");
        Console.WriteLine($"   EPC: {TEST_EPC}");
        Console.WriteLine();

        var result = _printer!.PrintRfidLabelRaw(TEST_EPC);
        if (result.Success)
        {
            Console.WriteLine();
            Console.WriteLine("✅ Etiqueta RFID enviada!");
            Console.WriteLine("   Verifica con un lector RFID que el EPC se escribió correctamente.");
        }
        else
        {
            Console.WriteLine($"❌ {result.Message}");
        }
    }

    private static void PrintRfidCustom()
    {
        if (!RequireConnection()) return;

        Console.WriteLine("📝 Ingresa los datos para la etiqueta RFID:");
        Console.WriteLine();

        Console.Write("   EPC (24 caracteres hex, ej: E20034120123456789ABCDEF): ");
        string epc = Console.ReadLine() ?? TEST_EPC;
        if (string.IsNullOrWhiteSpace(epc)) epc = TEST_EPC;

        Console.Write("   Texto de etiqueta: ");
        string text = Console.ReadLine() ?? "CUSTOM RFID";
        if (string.IsNullOrWhiteSpace(text)) text = "CUSTOM RFID";

        Console.Write("   Código de barras: ");
        string barcode = Console.ReadLine() ?? "123456789";
        if (string.IsNullOrWhiteSpace(barcode)) barcode = "123456789";

        Console.WriteLine();
        Console.WriteLine($"   Imprimiendo con EPC: {epc}");

        var result = _printer!.PrintRfidLabel(epc, text, barcode);
        Console.WriteLine(result.Success ? "✅ Etiqueta RFID personalizada enviada!" : $"❌ {result.Message}");
    }

    private static void SendManualCommand()
    {
        if (!RequireConnection()) return;

        Console.WriteLine("📝 Ingrese el comando ZPL (o 'test' para un comando de prueba):");
        Console.Write("> ");
        string command = Console.ReadLine() ?? "";

        if (command.ToLower() == "test")
        {
            command = "^XA^PW640^LL160^MNY^FO20,20^A0N,30,30^FDTEST MANUAL ZPL^FS^PQ1^XZ";
            Console.WriteLine($"Enviando comando de prueba:");
            Console.WriteLine(command);
        }

        if (!string.IsNullOrWhiteSpace(command))
        {
            var result = _printer!.SendRawCommand(command);
            Console.WriteLine(result.Success ? "✅ Comando enviado!" : $"❌ {result.Message}");
        }
    }
}
