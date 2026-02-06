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
/// Usando el SDK oficial UniPRT de TSC
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

    /// <summary>
    /// Constructor para conexión por red TCP/IP
    /// </summary>
    /// <param name="ipAddress">IP de la impresora (ej: 192.168.3.38)</param>
    /// <param name="port">Puerto TCP (default: 9100)</param>
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
                result.Add(((ushort)device.vendorID, (ushort)device.productID, $"VID:{device.vendorID:X4} PID:{device.productID:X4}"));
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
            if (_connectionType == ConnectionType.Ethernet)
            {
                return ConnectEthernet();
            }
            else
            {
                return ConnectUsb();
            }
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

        if (_isConnected)
        {
            Console.WriteLine("✅ Conexión Ethernet establecida");
        }
        else
        {
            Console.WriteLine("❌ No se pudo conectar por Ethernet");
        }

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
        {
            Console.WriteLine($"   [{i}] VID:{devices[i].vendorID:X4} PID:{devices[i].productID:X4}");
        }

        if (_usbDeviceIndex < 0 || _usbDeviceIndex >= devices.Count)
        {
            Console.WriteLine($"❌ Índice USB inválido: {_usbDeviceIndex}. Rango válido: 0..{devices.Count - 1}");
            return false;
        }

        // Usar el dispositivo seleccionado
        var device = devices[_usbDeviceIndex];
        Console.WriteLine($"📡 Conectando a dispositivo USB VID:{device.vendorID:X4} PID:{device.productID:X4}...");
        
        _usbConnection = new UsbConnection(device.vendorID, device.productID);
        _usbConnection.Open();
        
        _isConnected = _usbConnection.Connected;
        _connectionInfo = $"USB VID:{device.vendorID:X4} PID:{device.productID:X4}";

        if (_isConnected)
        {
            Console.WriteLine("✅ Conexión USB establecida");
        }
        else
        {
            Console.WriteLine("❌ No se pudo conectar por USB");
        }

        return _isConnected;
    }

    /// <summary>
    /// Verifica si la impresora está conectada
    /// </summary>
    public bool IsConnected
    {
        get
        {
            if (!_isConnected) return false;
            
            if (_connectionType == ConnectionType.Ethernet)
                return _tcpConnection?.Connected ?? false;
            else
                return _usbConnection?.Connected ?? false;
        }
    }

    /// <summary>
    /// Envía comandos TSPL a la impresora
    /// </summary>
    private bool SendCommand(string command)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        try
        {
            byte[] data = Encoding.ASCII.GetBytes(command);
            
            if (_connectionType == ConnectionType.Ethernet && _tcpConnection != null)
            {
                _tcpConnection.Write(data);
            }
            else if (_connectionType == ConnectionType.Usb && _usbConnection != null)
            {
                _usbConnection.Write(data);
            }
            else
            {
                return false;
            }
            
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error enviando comando: {ex.Message}");
            return false;
        }
    }

    /// <summary>
    /// Imprime una etiqueta RFID con EPC personalizado
    /// </summary>
    /// <param name="epcHex">Código EPC en hexadecimal (24 caracteres para 96 bits)</param>
    /// <param name="labelText">Texto a imprimir en la etiqueta</param>
    /// <param name="barcodeData">Datos del código de barras</param>
    public bool PrintRfidLabel(string epcHex, string labelText, string barcodeData)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        // Validar EPC (debe ser 24 caracteres hex para 96 bits)
        if (epcHex.Length != 24)
        {
            Console.WriteLine($"⚠️ Advertencia: EPC debería tener 24 caracteres hex (96 bits). Actual: {epcHex.Length}");
        }

        Console.WriteLine($"🏷️ Preparando etiqueta RFID...");
        Console.WriteLine($"   EPC: {epcHex}");
        Console.WriteLine($"   Texto: {labelText}");

        // Construir script TSPL completo
        string tsplScript = $@"SIZE 4,2
GAP 0.12,0
DIRECTION 1
CLS
RFIDDETECT AUTO
RFIDSETUP 0,5,2
RFIDENCODE EPC,0,96,""{epcHex}""
TEXT 50,30,""3"",0,1,1,""{labelText}""
TEXT 50,70,""2"",0,1,1,""EPC: {epcHex}""
BARCODE 50,120,""128"",60,1,0,2,2,""{barcodeData}""
PRINT 1,1
";

        if (SendCommand(tsplScript))
        {
            Console.WriteLine("✅ Etiqueta RFID enviada a impresora");
            return true;
        }

        return false;
    }

    /// <summary>
    /// Imprime etiqueta de prueba solo con texto (sin RFID)
    /// </summary>
    public bool PrintTestLabel(string text)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        Console.WriteLine($"🏷️ Imprimiendo etiqueta de prueba: {text}");

        string tsplScript = $@"SIZE 4,2
GAP 0.12,0
DIRECTION 1
CLS
TEXT 50,50,""4"",0,1,1,""{text}""
TEXT 50,100,""2"",0,1,1,""Prueba de conexion exitosa""
PRINT 1,1
";

        if (SendCommand(tsplScript))
        {
            Console.WriteLine("✅ Etiqueta de prueba enviada");
            return true;
        }

        return false;
    }

    /// <summary>
    /// Obtiene el estado de la impresora
    /// </summary>
    public string GetStatus()
    {
        if (!IsConnected)
        {
            return "❌ No conectado";
        }

        return $"✅ Conectado ({_connectionType}): {_connectionInfo}";
    }

    /// <summary>
    /// Desconecta de la impresora
    /// </summary>
    public void Disconnect()
    {
        try
        {
            if (_tcpConnection != null)
            {
                _tcpConnection.Close();
                _tcpConnection = null;
            }
            
            if (_usbConnection != null)
            {
                _usbConnection.Close();
                _usbConnection = null;
            }
            
            if (_isConnected)
            {
                Console.WriteLine("🔌 Desconectado de la impresora");
            }
        }
        catch { }
        
        _isConnected = false;
    }

    public void Dispose()
    {
        Disconnect();
    }
}
