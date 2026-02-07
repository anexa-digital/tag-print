using System.Text;
using UniPRT.Sdk.Comm;

namespace RfidTagPrinter;

/// <summary>
/// Tipo de conexión a la impresora
/// </summary>
public enum ConnectionType
{
    Ethernet,
    Usb
}

/// <summary>
/// Servicio para impresión de etiquetas RFID en Printronix T820
/// 
/// IMPORTANTE: La impresora DEBE estar en modo ZGL (ZPL emulation).
/// TGL NO soporta comandos RFID. ZGL sí (^RF, ^RB, ^RS, etc.)
/// 
/// Configurar en la impresora:
///   Settings > Application > Control > Active IGP Emul > ZGL
/// </summary>
public class RfidPrinterService : IDisposable
{
    private readonly string _printerIp;
    private readonly int _printerPort;
    private readonly ConnectionType _connectionType;
    private readonly int _usbDeviceIndex;
    
    private TcpConnection? _tcpConnection;
    private UsbConnection? _usbConnection;
    private bool _isConnected;
    private string _connectionInfo = "";

    // ==========================================
    // CONSTRUCTORES
    // ==========================================

    /// <summary>
    /// Constructor para conexión por red TCP/IP
    /// </summary>
    public RfidPrinterService(string ipAddress, int port = 9100)
    {
        _printerIp = ipAddress;
        _printerPort = port;
        _connectionType = ConnectionType.Ethernet;
    }

    /// <summary>
    /// Constructor para conexión por USB
    /// </summary>
    public RfidPrinterService(int usbDeviceIndex = 0)
    {
        _printerIp = "";
        _printerPort = 0;
        _connectionType = ConnectionType.Usb;
        _usbDeviceIndex = usbDeviceIndex;
    }

    // ==========================================
    // CONEXIÓN
    // ==========================================

    /// <summary>
    /// Lista los dispositivos USB disponibles
    /// </summary>
    public static List<(ushort vendorId, ushort productId, string description)> ListUsbDevices()
    {
        var result = new List<(ushort vendorId, ushort productId, string description)>();
        try
        {
            var devices = UsbConnection.AvaliableDevices();
            foreach (var device in devices)
            {
                result.Add(((ushort)device.vendorID, (ushort)device.productID, 
                    $"VID:{device.vendorID:X4} PID:{device.productID:X4}"));
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error listando dispositivos USB: {ex.Message}");
        }
        return result;
    }

    /// <summary>
    /// Conecta a la impresora
    /// </summary>
    public bool Connect()
    {
        try
        {
            return _connectionType == ConnectionType.Ethernet 
                ? ConnectEthernet() 
                : ConnectUsb();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error de conexión: {ex.Message}");
            _isConnected = false;
            return false;
        }
    }

    private bool ConnectEthernet()
    {
        Console.WriteLine($"📡 Conectando a {_printerIp}:{_printerPort}...");
        _tcpConnection = new TcpConnection(_printerIp, _printerPort);
        _tcpConnection.Open();
        _isConnected = _tcpConnection.Connected;
        _connectionInfo = $"{_printerIp}:{_printerPort}";
        Console.WriteLine(_isConnected ? "✅ Conexión Ethernet establecida" : "❌ No se pudo conectar");
        return _isConnected;
    }

    private bool ConnectUsb()
    {
        Console.WriteLine("🔌 Buscando impresoras USB...");
        var devices = UsbConnection.AvaliableDevices();
        if (devices.Count == 0)
        {
            Console.WriteLine("❌ No se encontraron impresoras USB");
            return false;
        }

        Console.WriteLine($"   Encontrados {devices.Count} dispositivo(s):");
        for (int i = 0; i < devices.Count; i++)
            Console.WriteLine($"   [{i}] VID:{devices[i].vendorID:X4} PID:{devices[i].productID:X4}");

        if (_usbDeviceIndex < 0 || _usbDeviceIndex >= devices.Count)
        {
            Console.WriteLine($"❌ Índice USB inválido: {_usbDeviceIndex}");
            return false;
        }

        var device = devices[_usbDeviceIndex];
        Console.WriteLine($"📡 Conectando USB VID:{device.vendorID:X4} PID:{device.productID:X4}...");
        _usbConnection = new UsbConnection(device.vendorID, device.productID);
        _usbConnection.Open();
        _isConnected = _usbConnection.Connected;
        _connectionInfo = $"USB VID:{device.vendorID:X4} PID:{device.productID:X4}";
        Console.WriteLine(_isConnected ? "✅ Conexión USB establecida" : "❌ No se pudo conectar");
        return _isConnected;
    }

    public bool IsConnected
    {
        get
        {
            if (!_isConnected) return false;
            return _connectionType == ConnectionType.Ethernet
                ? _tcpConnection?.Connected ?? false
                : _usbConnection?.Connected ?? false;
        }
    }

    // ==========================================
    // ENVÍO DE DATOS
    // ==========================================

    /// <summary>
    /// Envía bytes a la impresora
    /// </summary>
    private bool SendBytes(byte[] data)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        try
        {
            if (_connectionType == ConnectionType.Ethernet && _tcpConnection != null)
                _tcpConnection.Write(data);
            else if (_connectionType == ConnectionType.Usb && _usbConnection != null)
                _usbConnection.Write(data);
            else
                return false;
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error enviando datos: {ex.Message}");
            return false;
        }
    }

    /// <summary>
    /// Envía string como bytes ASCII a la impresora
    /// </summary>
    private bool SendCommand(string command)
    {
        return SendBytes(Encoding.ASCII.GetBytes(command));
    }

    // ==========================================
    // CONFIGURACIÓN DE ETIQUETA (ZPL)
    // ==========================================

    // Dimensiones reales de la etiqueta RFID (80mm x 20mm)
    // ZPL usa dots. A 203 dpi: 1mm ≈ 8 dots
    // 80mm ≈ 640 dots de ancho, 20mm ≈ 160 dots de alto
    private const int LABEL_WIDTH_DOTS = 640;   // 80mm @ 203dpi
    private const int LABEL_HEIGHT_DOTS = 160;  // 20mm @ 203dpi

    // ==========================================
    // MÉTODO 1: ZPL con RFID (^RF Write EPC)
    // ==========================================

    /// <summary>
    /// Imprime etiqueta RFID usando ZPL con comando ^RF para escribir EPC.
    /// REQUIERE: Impresora en modo ZGL (Settings > Application > Control > Active IGP Emul > ZGL)
    /// 
    /// Comando ^RF:
    ///   ^RFW,H = Write, formato Hex
    ///   ^FD{data} = datos hex del EPC
    /// </summary>
    public bool PrintRfidLabel(string epcHex, string labelText, string barcodeData)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        var normalizedEpc = NormalizeEpc(epcHex);
        if (normalizedEpc == null) return false;
        epcHex = normalizedEpc;

        Console.WriteLine($"🏷️ [ZPL + RFID] Preparando etiqueta RFID...");
        Console.WriteLine($"   EPC: {epcHex}");
        Console.WriteLine($"   Texto: {labelText}");
        Console.WriteLine($"   Código: {barcodeData}");
        Console.WriteLine($"   Etiqueta: {LABEL_WIDTH_DOTS}x{LABEL_HEIGHT_DOTS} dots (80x20mm)");

        try
        {
            var sb = new StringBuilder();
            sb.Append("^XA");                                              // Inicio formato
            sb.Append($"^PW{LABEL_WIDTH_DOTS}");                          // Ancho de impresión
            sb.Append($"^LL{LABEL_HEIGHT_DOTS}");                         // Largo de etiqueta
            sb.Append("^MNY");                                             // Gap/mark tracking
            // --- RFID: Escribir EPC ---
            sb.Append("^RS8");                                             // RFID setup: adaptive antenna
            sb.Append($"^RFW,H^FD{epcHex}^FS");                          // RFID Write EPC en hex
            // --- Contenido visual ---
            sb.Append($"^FO20,10^A0N,25,25^FD{labelText}^FS");           // Texto principal
            sb.Append($"^FO20,40^A0N,18,18^FDEPC: {epcHex}^FS");        // EPC como texto
            sb.Append($"^FO20,70^BCN,50,Y,N,N^FD{barcodeData}^FS");     // Code128 barcode
            sb.Append("^PQ1");                                             // Imprimir 1 etiqueta
            sb.Append("^XZ");                                              // Fin formato

            string zpl = sb.ToString();

            Console.WriteLine("📤 Script ZPL enviado:");
            Console.WriteLine("---");
            Console.WriteLine(zpl);
            Console.WriteLine("---");

            if (SendCommand(zpl))
            {
                Console.WriteLine("✅ Etiqueta RFID (ZPL) enviada a impresora");
                return true;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error: {ex.Message}");
            Console.WriteLine($"   Stack: {ex.StackTrace}");
        }

        return false;
    }

    // ==========================================
    // MÉTODO 2: ZPL solo RFID (mínimo, sin contenido visual)
    // ==========================================

    /// <summary>
    /// Imprime etiqueta RFID con ZPL mínimo: solo encode RFID + texto simple.
    /// Útil para depuración: si esto funciona, el RFID está bien configurado.
    /// </summary>
    public bool PrintRfidLabelRaw(string epcHex, string labelText, string barcodeData)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        var normalizedEpc = NormalizeEpc(epcHex);
        if (normalizedEpc == null) return false;
        epcHex = normalizedEpc;

        Console.WriteLine($"🏷️ [ZPL Mínimo] Solo RFID encode + texto simple...");
        Console.WriteLine($"   EPC: {epcHex}");

        try
        {
            var sb = new StringBuilder();
            sb.Append("^XA");                                              // Inicio formato
            sb.Append($"^PW{LABEL_WIDTH_DOTS}");                          // Ancho
            sb.Append($"^LL{LABEL_HEIGHT_DOTS}");                         // Largo
            sb.Append("^MNY");                                             // Gap tracking
            // --- RFID: Solo escribir EPC ---
            sb.Append("^RS8");                                             // RFID setup
            sb.Append($"^RFW,H^FD{epcHex}^FS");                          // RFID Write EPC
            // --- Texto mínimo ---
            sb.Append($"^FO20,20^A0N,30,30^FDRFID OK^FS");               // Solo un texto
            sb.Append("^PQ1");                                             // 1 copia
            sb.Append("^XZ");                                              // Fin formato

            string zpl = sb.ToString();

            Console.WriteLine("📤 Script ZPL enviado:");
            Console.WriteLine("---");
            Console.WriteLine(zpl);
            Console.WriteLine("---");

            if (SendCommand(zpl))
            {
                Console.WriteLine("✅ Etiqueta RFID mínima enviada a impresora");
                return true;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error: {ex.Message}");
            Console.WriteLine($"   Stack: {ex.StackTrace}");
        }

        return false;
    }

    // ==========================================
    // ETIQUETA DE PRUEBA (sin RFID, ZPL)
    // ==========================================
    /// <summary>
    /// Imprime etiqueta de prueba (sin RFID) con ZPL puro.
    /// Sirve para verificar que ZGL está bien configurado.
    /// </summary>
    public bool PrintTestLabel(string text)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        Console.WriteLine($"🏷️ Imprimiendo etiqueta de prueba (ZPL): {text}");

        try
        {
            var sb = new StringBuilder();
            sb.Append("^XA");
            sb.Append($"^PW{LABEL_WIDTH_DOTS}");
            sb.Append($"^LL{LABEL_HEIGHT_DOTS}");
            sb.Append("^MNY");
            sb.Append($"^FO20,15^A0N,30,30^FD{text}^FS");
            sb.Append("^FO20,55^A0N,20,20^FDPrueba de conexion exitosa (ZPL)^FS");
            sb.Append("^PQ1");
            sb.Append("^XZ");

            string zpl = sb.ToString();
            Console.WriteLine("📤 Script ZPL generado:");
            Console.WriteLine(zpl);

            if (SendCommand(zpl))
            {
                Console.WriteLine("✅ Etiqueta de prueba (ZPL) enviada");
                return true;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error: {ex.Message}");
        }

        return false;
    }

    /// <summary>
    /// Envía un comando ZPL/raw sin procesar
    /// </summary>
    public bool SendRawCommand(string command)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }
        return SendCommand(command);
    }

    // ==========================================
    // UTILIDADES
    // ==========================================

    /// <summary>
    /// Normaliza y valida el EPC hex
    /// </summary>
    private string? NormalizeEpc(string epcHex)
    {
        epcHex = epcHex.ToUpper().Replace(" ", "");
        
        if (!System.Text.RegularExpressions.Regex.IsMatch(epcHex, "^[0-9A-F]+$"))
        {
            Console.WriteLine("❌ Error: EPC contiene caracteres no hexadecimales");
            return null;
        }

        if (epcHex.Length < 24)
        {
            epcHex = epcHex.PadRight(24, '0');
            Console.WriteLine($"⚠️ EPC rellenado a 24 chars: {epcHex}");
        }
        else if (epcHex.Length > 24)
        {
            epcHex = epcHex.Substring(0, 24);
            Console.WriteLine($"⚠️ EPC truncado a 24 chars: {epcHex}");
        }

        return epcHex;
    }

    public string GetStatus()
    {
        return IsConnected 
            ? $"✅ Conectado ({_connectionType}): {_connectionInfo}" 
            : "❌ No conectado";
    }

    public void Disconnect()
    {
        try
        {
            _tcpConnection?.Close();
            _tcpConnection = null;
            _usbConnection?.Close();
            _usbConnection = null;
            if (_isConnected)
                Console.WriteLine("🔌 Desconectado de la impresora");
        }
        catch { }
        _isConnected = false;
    }

    public void Dispose() => Disconnect();
}
