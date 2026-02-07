using System.Text;
using UniPRT.Sdk.Comm;
using UniPRT.Sdk.LabelMaker.TSPL;
using UniPRT.Sdk.LabelMaker.Interfaces;

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
/// Usando el SDK oficial UniPRT de TSC (LabelMaker API)
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
    // CONFIGURACIÓN DE ETIQUETA
    // ==========================================

    // Dimensiones reales de la etiqueta RFID (80mm x 20mm)
    private const string LABEL_WIDTH_MM = "80";
    private const string LABEL_HEIGHT_MM = "20";
    private const string LABEL_GAP_MM = "3";  // gap entre etiquetas en mm

    // ==========================================
    // MÉTODO 1: HÍBRIDO (SDK RfidWrite + TSPL limpio)
    // ==========================================

    /// <summary>
    /// Imprime etiqueta RFID usando el comando RFID del SDK (RfidWrite.ToString())
    /// combinado con TSPL puro para el resto (sin variables ni boilerplate del SDK).
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

        Console.WriteLine($"🏷️ [Híbrido] Preparando etiqueta RFID...");
        Console.WriteLine($"   EPC: {epcHex}");
        Console.WriteLine($"   Texto: {labelText}");
        Console.WriteLine($"   Tamaño: {LABEL_WIDTH_MM}mm x {LABEL_HEIGHT_MM}mm");

        try
        {
            // Obtener comando RFID del SDK (ya validado por la API oficial)
            var rfidWrite = new RfidWrite(RfidMemBlockEnum.EPC, epcHex);
            string rfidCommand = rfidWrite.ToString();

            Console.WriteLine($"   RFID CMD (SDK): {rfidCommand.Trim()}");

            // Construir TSPL limpio (sin variables, sin boilerplate)
            var sb = new StringBuilder();
            sb.AppendLine($"SIZE {LABEL_WIDTH_MM} mm,{LABEL_HEIGHT_MM} mm");
            sb.AppendLine($"GAP {LABEL_GAP_MM} mm,0");
            sb.AppendLine("DIRECTION 1");
            sb.AppendLine("CLS");
            sb.Append(rfidCommand);  // SDK genera: RFID WRITE 0,H,0,96,EPC,"data"\n
            sb.AppendLine($"TEXT 30,10,\"2\",0,1,1,\"{labelText}\"");
            sb.AppendLine($"TEXT 30,45,\"1\",0,1,1,\"EPC: {epcHex}\"");
            sb.AppendLine($"BARCODE 30,70,\"128\",40,1,0,2,2,\"{barcodeData}\"");
            sb.AppendLine("PRINT 1,1");

            string tspl = sb.ToString();

            Console.WriteLine("📤 Script TSPL enviado:");
            Console.WriteLine("---");
            Console.Write(tspl);
            Console.WriteLine("---");

            if (SendCommand(tspl))
            {
                Console.WriteLine("✅ Etiqueta RFID enviada a impresora");
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
    // MÉTODO 2: TSPL PURO (sin SDK, comando RFID directo)
    // ==========================================

    /// <summary>
    /// Imprime etiqueta RFID usando TSPL 100% puro.
    /// Usa la sintaxis RFID WRITE descubierta del SDK sin depender de él.
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

        int epcBits = epcHex.Length * 4;  // 24 hex chars = 96 bits

        Console.WriteLine($"🏷️ [TSPL Puro] Preparando etiqueta RFID...");
        Console.WriteLine($"   EPC: {epcHex} ({epcBits} bits)");
        Console.WriteLine($"   Texto: {labelText}");

        try
        {
            var sb = new StringBuilder();
            sb.AppendLine($"SIZE {LABEL_WIDTH_MM} mm,{LABEL_HEIGHT_MM} mm");
            sb.AppendLine($"GAP {LABEL_GAP_MM} mm,0");
            sb.AppendLine("DIRECTION 1");
            sb.AppendLine("CLS");
            // Comando RFID WRITE: retry=0, format=H(hex), offset=0, bits=96, bank=EPC
            sb.AppendLine($"RFID WRITE 0,H,0,{epcBits},EPC,\"{epcHex}\"");
            sb.AppendLine($"TEXT 30,10,\"2\",0,1,1,\"{labelText}\"");
            sb.AppendLine($"TEXT 30,45,\"1\",0,1,1,\"EPC: {epcHex}\"");
            sb.AppendLine($"BARCODE 30,70,\"128\",40,1,0,2,2,\"{barcodeData}\"");
            sb.AppendLine("PRINT 1,1");

            string tspl = sb.ToString();

            Console.WriteLine("📤 Script TSPL enviado:");
            Console.WriteLine("---");
            Console.Write(tspl);
            Console.WriteLine("---");

            if (SendCommand(tspl))
            {
                Console.WriteLine("✅ Etiqueta RFID enviada a impresora");
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
    // ETIQUETA DE PRUEBA (sin RFID)
    // ==========================================
    /// <summary>
    /// Imprime etiqueta de prueba (sin RFID) con TSPL puro
    /// </summary>
    public bool PrintTestLabel(string text)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        Console.WriteLine($"🏷️ Imprimiendo etiqueta de prueba: {text}");

        try
        {
            var sb = new StringBuilder();
            sb.AppendLine($"SIZE {LABEL_WIDTH_MM} mm,{LABEL_HEIGHT_MM} mm");
            sb.AppendLine($"GAP {LABEL_GAP_MM} mm,0");
            sb.AppendLine("DIRECTION 1");
            sb.AppendLine("CLS");
            sb.AppendLine($"TEXT 30,15,\"2\",0,1,1,\"{text}\"");
            sb.AppendLine($"TEXT 30,50,\"1\",0,1,1,\"Prueba de conexion exitosa\"");
            sb.AppendLine("PRINT 1,1");

            string tspl = sb.ToString();
            Console.WriteLine("📤 Script generado:");
            Console.Write(tspl);

            if (SendCommand(tspl))
            {
                Console.WriteLine("✅ Etiqueta de prueba enviada");
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
    /// Envía un comando TSPL sin procesar
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
