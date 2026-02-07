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
    // IMPRESIÓN CON API LabelMaker (OFICIAL SDK)
    // ==========================================

    /// <summary>
    /// Imprime etiqueta RFID usando la API oficial del SDK (LabelMaker + RfidWrite)
    /// </summary>
    /// <param name="epcHex">EPC en hexadecimal (24 chars = 96 bits)</param>
    /// <param name="labelText">Texto visible en la etiqueta</param>
    /// <param name="barcodeData">Datos del código de barras</param>
    public bool PrintRfidLabel(string epcHex, string labelText, string barcodeData)
    {
        if (!IsConnected)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        // Limpiar y validar EPC
        var normalizedEpc = NormalizeEpc(epcHex);
        if (normalizedEpc == null) return false;
        epcHex = normalizedEpc;

        Console.WriteLine($"🏷️ Preparando etiqueta RFID (SDK LabelMaker)...");
        Console.WriteLine($"   EPC: {epcHex}");
        Console.WriteLine($"   Texto: {labelText}");

        try
        {
            // 1) Crear Label TSPL
            var label = new Label("RfidLabel");

            // 2) Agregar configuración de etiqueta via raw content
            label.AddRawContent("SIZE 4,2");
            label.AddRawContent("GAP 0.12,0");
            label.AddRawContent("DIRECTION 1");
            label.AddRawContent("CLS");

            // 3) Agregar RFID Write usando la API oficial del SDK
            var rfidWrite = new RfidWrite(RfidMemBlockEnum.EPC, epcHex);
            label.AddObject(rfidWrite);

            // 4) Agregar texto usando la API del SDK
            var textTitle = new TextItem(50f, 30f, labelText);
            var text = new Text(textTitle);
            label.AddObject(text);

            var textEpc = new TextItem(50f, 80f, $"EPC: {epcHex}");
            var text2 = new Text(textEpc);
            label.AddObject(text2);

            // 5) Agregar código de barras
            var barcodeItem = new BarcodeItem(50f, 130f, barcodeData);
            var barcode = new Barcode1D(barcodeItem);
            label.AddObject(barcode);

            // 6) Agregar comando PRINT
            label.AddRawContent("PRINT 1,1");

            // 7) Generar script TSPL completo
            string tsplOutput = label.ToString();

            Console.WriteLine("📤 Script TSPL generado por SDK:");
            Console.WriteLine("---");
            Console.WriteLine(tsplOutput);
            Console.WriteLine("---");

            // 8) Enviar a impresora
            if (SendCommand(tsplOutput))
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

    /// <summary>
    /// Imprime etiqueta de prueba (sin RFID) usando SDK LabelMaker
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
            var label = new Label("TestLabel");
            label.AddRawContent("SIZE 4,2");
            label.AddRawContent("GAP 0.12,0");
            label.AddRawContent("DIRECTION 1");
            label.AddRawContent("CLS");

            var textItem1 = new TextItem(50f, 50f, text);
            label.AddObject(new Text(textItem1));

            var textItem2 = new TextItem(50f, 100f, "Prueba de conexion exitosa");
            label.AddObject(new Text(textItem2));

            label.AddRawContent("PRINT 1,1");

            string tsplOutput = label.ToString();
            Console.WriteLine("📤 Script generado:");
            Console.WriteLine(tsplOutput);

            if (SendCommand(tsplOutput))
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
