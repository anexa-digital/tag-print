using System.Text;
using UniPRT.Sdk.Comm;

namespace RfidTagPrinter;

/// <summary>
/// Servicio para impresión de etiquetas RFID en Printronix T820
/// Usando el SDK oficial UniPRT de TSC
/// </summary>
public class RfidPrinterService : IDisposable
{
    private readonly string _printerIp;
    private readonly int _printerPort;
    private TcpConnection? _connection;
    private bool _isConnected;

    /// <summary>
    /// Constructor para conexión por red TCP/IP
    /// </summary>
    /// <param name="ipAddress">IP de la impresora (ej: 192.168.3.60)</param>
    /// <param name="port">Puerto TCP (default: 9100)</param>
    public RfidPrinterService(string ipAddress, int port = 9100)
    {
        _printerIp = ipAddress;
        _printerPort = port;
    }

    /// <summary>
    /// Conecta a la impresora
    /// </summary>
    public bool Connect()
    {
        try
        {
            Console.WriteLine($"📡 Conectando a {_printerIp}:{_printerPort}...");
            
            _connection = new TcpConnection(_printerIp, _printerPort);
            _connection.Open();
            
            _isConnected = _connection.Connected;

            if (_isConnected)
            {
                Console.WriteLine("✅ Conexión establecida");
            }
            else
            {
                Console.WriteLine("❌ No se pudo conectar");
            }

            return _isConnected;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error de conexión: {ex.Message}");
            _isConnected = false;
            return false;
        }
    }

    /// <summary>
    /// Verifica si la impresora está conectada
    /// </summary>
    public bool IsConnected => _isConnected && (_connection?.Connected ?? false);

    /// <summary>
    /// Envía comandos TSPL a la impresora
    /// </summary>
    private bool SendCommand(string command)
    {
        if (!IsConnected || _connection == null)
        {
            Console.WriteLine("❌ No conectado a la impresora");
            return false;
        }

        try
        {
            byte[] data = Encoding.ASCII.GetBytes(command);
            _connection.Write(data);
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

        return "✅ Conectado a " + _printerIp;
    }

    /// <summary>
    /// Desconecta de la impresora
    /// </summary>
    public void Disconnect()
    {
        if (_connection != null)
        {
            try
            {
                _connection.Close();
                Console.WriteLine("🔌 Desconectado de la impresora");
            }
            catch { }
            
            _connection = null;
            _isConnected = false;
        }
    }

    public void Dispose()
    {
        Disconnect();
    }
}
