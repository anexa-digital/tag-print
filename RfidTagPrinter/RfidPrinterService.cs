using System.Text;
using System.Text.RegularExpressions;
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
/// Resultado de una operación de impresión
/// </summary>
public record PrintResult(bool Success, string Message, string? ZplSent = null);

/// <summary>
/// Servicio para impresión de etiquetas RFID en Printronix T820
/// 
/// IMPORTANTE: La impresora DEBE estar en modo ZGL (ZPL emulation).
/// TGL NO soporta comandos RFID. ZGL sí (^RF, ^RB, ^RS, etc.)
/// 
/// Configurar en la impresora:
///   Settings > Application > Control > Active IGP Emul > ZGL
/// 
/// Soporta dos modos:
///   1. Conexión persistente (para modo consola interactivo)
///   2. Conexión on-demand (para API: conecta, ejecuta, desconecta)
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
    // CONFIGURACIÓN DE ETIQUETA (ZPL)
    // ==========================================

    // Dimensiones reales de la etiqueta RFID
    // Medidas físicas: 80mm ancho x 20mm alto, gap 3mm, margen derecho 5mm
    // ZPL usa dots. A 203 dpi: 1mm = 203/25.4 ≈ 7.99 dots ≈ 8 dots
    private const int LABEL_WIDTH_DOTS = 640;   // 80mm @ 203dpi
    private const int LABEL_HEIGHT_DOTS = 160;  // 20mm @ 203dpi
    private const int GAP_DOTS = 24;            // 3mm gap @ 203dpi
    private const int RIGHT_MARGIN_DOTS = 40;   // 5mm margen derecho @ 203dpi
    private const int PRINTABLE_WIDTH_DOTS = LABEL_WIDTH_DOTS - RIGHT_MARGIN_DOTS; // 600 dots (75mm)

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
    // CONEXIÓN ON-DEMAND (para API)
    // ==========================================

    /// <summary>
    /// Ejecuta una acción con una conexión TCP temporal (on-demand).
    /// Abre conexión, ejecuta la acción, y cierra la conexión.
    /// Ideal para uso desde la API donde cada request es independiente.
    /// </summary>
    public static PrintResult ExecuteWithConnection(string ip, int port, Func<RfidPrinterService, PrintResult> action)
    {
        using var service = new RfidPrinterService(ip, port);
        if (!service.Connect())
            return new PrintResult(false, $"No se pudo conectar a {ip}:{port}");

        try
        {
            return action(service);
        }
        finally
        {
            service.Disconnect();
        }
    }

    // ==========================================
    // CONEXIÓN PERSISTENTE (para modo consola)
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
    // ZPL BUILDERS (estáticos, reutilizables)
    // ==========================================

    /// <summary>
    /// Genera el ZPL para una etiqueta RFID completa (texto + barcode + RFID).
    /// </summary>
    public static string BuildRfidLabelZpl(string epcHex, string labelText, string barcodeData)
    {
        int epcBytes = epcHex.Length / 2;
        var sb = new StringBuilder();
        sb.Append("^XA");
        sb.Append($"^PW{LABEL_WIDTH_DOTS}");
        sb.Append($"^LL{LABEL_HEIGHT_DOTS}");
        sb.Append("^MNY");
        sb.Append("^RS8,0,0,0,0,0");
        sb.Append("^RR3");
        sb.Append($"^RFW,H,2,{epcBytes}^FD{epcHex}^FS");
        sb.Append($"^FO16,8^A0N,32,24^FD{labelText}^FS");
        sb.Append($"^FO16,48^A0N,20,16^FDEPC: {epcHex}^FS");
        sb.Append($"^FO16,76^BCN,30,Y,N,N^FD{barcodeData}^FS");
        sb.Append("^PQ1");
        sb.Append("^XZ");
        return sb.ToString();
    }

    /// <summary>
    /// Genera el ZPL para una etiqueta RFID mínima (solo encode + texto simple).
    /// </summary>
    public static string BuildRfidMinimalZpl(string epcHex)
    {
        int epcBytes = epcHex.Length / 2;
        var sb = new StringBuilder();
        sb.Append("^XA");
        sb.Append($"^PW{LABEL_WIDTH_DOTS}");
        sb.Append($"^LL{LABEL_HEIGHT_DOTS}");
        sb.Append("^MNY");
        sb.Append("^RS8,0,0,0,0,0");
        sb.Append("^RR3");
        sb.Append($"^RFW,H,2,{epcBytes}^FD{epcHex}^FS");
        sb.Append("^FO16,40^A0N,30,25^FDRFID OK^FS");
        sb.Append("^PQ1");
        sb.Append("^XZ");
        return sb.ToString();
    }

    /// <summary>
    /// Genera el ZPL para una etiqueta de prueba (sin RFID).
    /// </summary>
    public static string BuildTestLabelZpl(string text)
    {
        var sb = new StringBuilder();
        sb.Append("^XA");
        sb.Append($"^PW{LABEL_WIDTH_DOTS}");
        sb.Append($"^LL{LABEL_HEIGHT_DOTS}");
        sb.Append("^MNY");
        sb.Append($"^FO16,15^A0N,28,22^FD{text}^FS");
        sb.Append("^FO16,55^A0N,18,16^FDConexion OK (ZPL/ZGL)^FS");
        sb.Append("^PQ1");
        sb.Append("^XZ");
        return sb.ToString();
    }

    /// <summary>
    /// Genera el ZPL de calibración de media.
    /// </summary>
    public static string BuildCalibrationZpl()
    {
        var sb = new StringBuilder();
        sb.Append("^XA");
        sb.Append("^MNY");
        sb.Append($"^PW{LABEL_WIDTH_DOTS}");
        sb.Append($"^LL{LABEL_HEIGHT_DOTS}");
        sb.Append("^JUS");
        sb.Append("^XZ");
        return sb.ToString();
    }

    // ==========================================
    // MÉTODOS DE IMPRESIÓN (usan conexión actual)
    // ==========================================

    /// <summary>
    /// Imprime etiqueta RFID usando ZPL con comando ^RF para escribir EPC.
    /// </summary>
    public PrintResult PrintRfidLabel(string epcHex, string labelText, string barcodeData)
    {
        var normalizedEpc = EpcEncoder.NormalizeEpc(epcHex);
        if (normalizedEpc == null)
            return new PrintResult(false, "EPC contiene caracteres no hexadecimales");
        epcHex = normalizedEpc;

        var zpl = BuildRfidLabelZpl(epcHex, labelText, barcodeData);

        if (SendCommand(zpl))
            return new PrintResult(true, "Etiqueta RFID (ZPL) enviada a impresora", zpl);

        return new PrintResult(false, "Error enviando etiqueta RFID a la impresora");
    }

    /// <summary>
    /// Imprime etiqueta RFID con ZPL mínimo: solo encode RFID + texto simple.
    /// </summary>
    public PrintResult PrintRfidLabelRaw(string epcHex)
    {
        var normalizedEpc = EpcEncoder.NormalizeEpc(epcHex);
        if (normalizedEpc == null)
            return new PrintResult(false, "EPC contiene caracteres no hexadecimales");
        epcHex = normalizedEpc;

        var zpl = BuildRfidMinimalZpl(epcHex);

        if (SendCommand(zpl))
            return new PrintResult(true, "Etiqueta RFID mínima enviada a impresora", zpl);

        return new PrintResult(false, "Error enviando etiqueta RFID mínima a la impresora");
    }

    /// <summary>
    /// Imprime etiqueta de prueba (sin RFID) con ZPL puro.
    /// </summary>
    public PrintResult PrintTestLabel(string text)
    {
        var zpl = BuildTestLabelZpl(text);

        if (SendCommand(zpl))
            return new PrintResult(true, "Etiqueta de prueba (ZPL) enviada", zpl);

        return new PrintResult(false, "Error enviando etiqueta de prueba");
    }

    /// <summary>
    /// Calibra el media (gap sensing) de la impresora.
    /// </summary>
    public PrintResult CalibrateMedia()
    {
        var setupZpl = BuildCalibrationZpl();
        SendCommand(setupZpl);
        SendCommand("~JC");
        return new PrintResult(true, "Calibración enviada. Espera a que la impresora termine de avanzar.");
    }

    /// <summary>
    /// Envía un comando ZPL/raw sin procesar
    /// </summary>
    public PrintResult SendRawCommand(string command)
    {
        if (SendCommand(command))
            return new PrintResult(true, "Comando enviado", command);

        return new PrintResult(false, "Error enviando comando");
    }

    // ==========================================
    // UTILIDADES
    // ==========================================

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
