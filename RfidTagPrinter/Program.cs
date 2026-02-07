namespace RfidTagPrinter;

/// <summary>
/// Programa de prueba para impresión RFID en Printronix T820
/// Usando ZPL (modo ZGL) para RFID + SDK UniPRT para conexión
/// 
/// ANTES DE EJECUTAR:
/// 1. Cambiar lenguaje de impresora a ZGL: 
///    Settings > Application > Control > Active IGP Emul > ZGL
///    (TGL NO soporta RFID - solo ZGL y PGL tienen comandos RFID)
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
        Console.WriteLine("     Modo: ZGL (ZPL) + UniPRT SDK (conexión)              ");
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
                case '1':
                    ConnectEthernet();
                    break;

                case '2':
                    ConnectUsb();
                    break;

                case '3':
                    CalibrateMedia();
                    break;

                case '4':
                    PrintSimpleTest();
                    break;

                case '5':
                    PrintRfidTestHybrid();
                    break;

                case '6':
                    PrintRfidTestRaw();
                    break;

                case '7':
                    PrintRfidCustom();
                    break;

                case '8':
                    DisconnectPrinter();
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
            Console.WriteLine("   - Que el lenguaje esté en ZGL (no TGL ni PGL)");
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
            Console.WriteLine("   - Que el lenguaje esté en ZGL");
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

    static void CalibrateMedia()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
        Console.WriteLine("📏 Calibrando media...");
        Console.WriteLine("   La impresora avanzará algunas etiquetas para detectar el gap.");
        Console.WriteLine("   Esto es NECESARIO tras cambiar de TGL a ZGL.");
        Console.WriteLine();

        if (_printer.CalibrateMedia())
        {
            Console.WriteLine("✅ Calibración enviada. Espera a que la impresora termine de avanzar.");
        }
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

    static void PrintRfidTestHybrid()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
        Console.WriteLine("🏷️ [ZPL Completo] RFID + texto + barcode");
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

    static void PrintRfidTestRaw()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
        Console.WriteLine("🏷️ [ZPL Mínimo] Solo RFID encode - para depuración");
        Console.WriteLine($"   EPC: {TEST_EPC}");
        Console.WriteLine($"   Texto: {TEST_LABEL_TEXT}");
        Console.WriteLine($"   Código: {TEST_BARCODE}");
        Console.WriteLine();

        if (_printer.PrintRfidLabelRaw(TEST_EPC, TEST_LABEL_TEXT, TEST_BARCODE))
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

    static void SendManualCommand()
    {
        if (_printer == null || !_printer.IsConnected)
        {
            Console.WriteLine("❌ No hay conexión. Use opción 1 o 2 para conectar.");
            return;
        }
        
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
            if (_printer.SendRawCommand(command))
            {
                Console.WriteLine("✅ Comando enviado!");
            }
        }
    }
}
