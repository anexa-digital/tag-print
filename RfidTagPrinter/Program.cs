using RfidTagPrinter;

// ============================================
// DUAL MODE: API (default) o Consola (--console)
// ============================================

if (args.Contains("--console"))
{
    ConsoleMode.Run(args);
    return;
}

// ============================================
// MINIMAL API
// ============================================

var builder = WebApplication.CreateBuilder(args);

// Configuración: env vars override appsettings.json
builder.Configuration.AddEnvironmentVariables();

var app = builder.Build();

// Leer configuración de impresora
var printerIp = app.Configuration["PRINTER_IP"]
    ?? app.Configuration["Printer:Ip"]
    ?? "192.168.3.38";
var printerPort = int.TryParse(
    app.Configuration["PRINTER_PORT"] ?? app.Configuration["Printer:Port"],
    out var p) ? p : 9100;

app.Logger.LogInformation("RFID Tag Printer API iniciada");
app.Logger.LogInformation("Impresora configurada: {Ip}:{Port}", printerIp, printerPort);

// API Key middleware (excluye /health)
app.UseMiddleware<ApiKeyMiddleware>();

// ============================================
// ENDPOINTS
// ============================================

// --- Health check (sin API key) ---
app.MapGet("/health", () => Results.Ok(new
{
    status = "healthy",
    service = "rfid-tag-printer",
    printer = new { ip = printerIp, port = printerPort }
}));

// --- Estado ---
app.MapGet("/api/v1/status", () =>
{
    // Test rápido de conectividad TCP
    try
    {
        var result = RfidPrinterService.ExecuteWithConnection(printerIp, printerPort, svc =>
            new PrintResult(true, svc.GetStatus()));
        return Results.Ok(new { connected = result.Success, message = result.Message });
    }
    catch (Exception ex)
    {
        return Results.Ok(new { connected = false, message = ex.Message });
    }
});

// --- Imprimir RFID completo ---
app.MapPost("/api/v1/print/rfid", (RfidPrintRequest req) =>
{
    if (string.IsNullOrWhiteSpace(req.EpcHex))
        return Results.BadRequest(new { error = "epcHex es requerido" });
    if (string.IsNullOrWhiteSpace(req.LabelText))
        return Results.BadRequest(new { error = "labelText es requerido" });
    if (string.IsNullOrWhiteSpace(req.BarcodeData))
        return Results.BadRequest(new { error = "barcodeData es requerido" });

    var result = RfidPrinterService.ExecuteWithConnection(printerIp, printerPort, svc =>
        svc.PrintRfidLabel(req.EpcHex, req.LabelText, req.BarcodeData));

    return result.Success
        ? Results.Ok(new { success = true, message = result.Message, zpl = result.ZplSent })
        : Results.Json(new { success = false, error = result.Message }, statusCode: 502);
});

// --- Imprimir RFID mínimo ---
app.MapPost("/api/v1/print/rfid-minimal", (RfidMinimalRequest req) =>
{
    if (string.IsNullOrWhiteSpace(req.EpcHex))
        return Results.BadRequest(new { error = "epcHex es requerido" });

    var result = RfidPrinterService.ExecuteWithConnection(printerIp, printerPort, svc =>
        svc.PrintRfidLabelRaw(req.EpcHex));

    return result.Success
        ? Results.Ok(new { success = true, message = result.Message, zpl = result.ZplSent })
        : Results.Json(new { success = false, error = result.Message }, statusCode: 502);
});

// --- Imprimir etiqueta de prueba ---
app.MapPost("/api/v1/print/test", (TestPrintRequest? req) =>
{
    var text = req?.Text ?? "TEST API";

    var result = RfidPrinterService.ExecuteWithConnection(printerIp, printerPort, svc =>
        svc.PrintTestLabel(text));

    return result.Success
        ? Results.Ok(new { success = true, message = result.Message, zpl = result.ZplSent })
        : Results.Json(new { success = false, error = result.Message }, statusCode: 502);
});

// --- Calibrar media ---
app.MapPost("/api/v1/calibrate", () =>
{
    var result = RfidPrinterService.ExecuteWithConnection(printerIp, printerPort, svc =>
        svc.CalibrateMedia());

    return result.Success
        ? Results.Ok(new { success = true, message = result.Message })
        : Results.Json(new { success = false, error = result.Message }, statusCode: 502);
});

// --- Enviar ZPL raw ---
app.MapPost("/api/v1/print/raw", (RawZplRequest req) =>
{
    if (string.IsNullOrWhiteSpace(req.Zpl))
        return Results.BadRequest(new { error = "zpl es requerido" });

    var result = RfidPrinterService.ExecuteWithConnection(printerIp, printerPort, svc =>
        svc.SendRawCommand(req.Zpl));

    return result.Success
        ? Results.Ok(new { success = true, message = result.Message })
        : Results.Json(new { success = false, error = result.Message }, statusCode: 502);
});

// --- Codificar código de despacho → EPC hex ---
app.MapPost("/api/v1/epc/encode", (EpcEncodeRequest req) =>
{
    if (string.IsNullOrWhiteSpace(req.DispatchCode))
        return Results.BadRequest(new { error = "dispatchCode es requerido (ej: PVE-219836-WAR-3270806)" });

    var result = EpcEncoder.Encode(req.DispatchCode);

    return result.Success
        ? Results.Ok(new { success = true, epcHex = result.EpcHex, dispatchCode = result.DispatchCode })
        : Results.BadRequest(new { success = false, error = result.Error });
});

// --- Decodificar EPC hex → código de despacho ---
app.MapPost("/api/v1/epc/decode", (EpcDecodeRequest req) =>
{
    if (string.IsNullOrWhiteSpace(req.EpcHex))
        return Results.BadRequest(new { error = "epcHex es requerido (24 chars hex)" });

    var result = EpcEncoder.Decode(req.EpcHex);

    return result.Success
        ? Results.Ok(new { success = true, dispatchCode = result.DispatchCode, epcHex = result.EpcHex, version = result.Version })
        : Results.BadRequest(new { success = false, error = result.Error });
});

app.Run();

// ============================================
// REQUEST DTOs
// ============================================

public record RfidPrintRequest(string EpcHex, string LabelText, string BarcodeData);
public record RfidMinimalRequest(string EpcHex);
public record TestPrintRequest(string? Text);
public record RawZplRequest(string Zpl);
public record EpcEncodeRequest(string DispatchCode);
public record EpcDecodeRequest(string EpcHex);
