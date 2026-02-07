using System.Text.RegularExpressions;

namespace RfidTagPrinter;

/// <summary>
/// Codificador/Decodificador EPC para Empacor RFID.
/// 
/// Esquema para codificar códigos de despacho tipo "PVE-219836-WAR-3270806"
/// en los 96 bits (12 bytes = 24 caracteres hex) del EPC de un tag RFID UHF.
/// 
/// Estructura (24 hex chars):
///   Pos 0-1:   Formato/versión (EA = v1)
///   Pos 2-3:   Prefijo tipo documento (AA=PVE, AB=PVZ, AC=PVI)
///   Pos 4-12:  Número 1 (9 dígitos, zero-pad)
///   Pos 13-14: Prefijo tipo ubicación (BA=DIR, BB=WAR, BC=DEV, BD=AJU)
///   Pos 15-23: Número 2 (9 dígitos, zero-pad)
/// 
/// Ejemplo: PVE-219836-WAR-3270806 → EAAA000219836BB003270806
/// </summary>
public static class EpcEncoder
{
    private const string FormatVersion = "EA"; // Empacor formato v1

    // Prefijo 1 — Tipo de documento
    private static readonly Dictionary<string, string> DocTypeToHex = new()
    {
        ["PVE"] = "AA",
        ["PVZ"] = "AB",
        ["PVI"] = "AC",
    };

    private static readonly Dictionary<string, string> HexToDocType =
        DocTypeToHex.ToDictionary(kv => kv.Value, kv => kv.Key);

    // Prefijo 2 — Tipo de ubicación
    private static readonly Dictionary<string, string> LocTypeToHex = new()
    {
        ["DIR"] = "BA",
        ["WAR"] = "BB",
        ["DEV"] = "BC",
        ["AJU"] = "BD",
    };

    private static readonly Dictionary<string, string> HexToLocType =
        LocTypeToHex.ToDictionary(kv => kv.Value, kv => kv.Key);

    /// <summary>
    /// Codifica un código de despacho a EPC hex de 24 caracteres.
    /// Entrada: "PVE-219836-WAR-3270806"
    /// Salida:  "EAAA000219836BB003270806"
    /// </summary>
    public static EpcEncodeResult Encode(string dispatchCode)
    {
        if (string.IsNullOrWhiteSpace(dispatchCode))
            return EpcEncodeResult.Fail("Código de despacho vacío");

        var code = dispatchCode.Trim().ToUpper();
        var parts = code.Split('-');

        if (parts.Length != 4)
            return EpcEncodeResult.Fail(
                $"Se esperan 4 partes separadas por guiones, se obtuvieron {parts.Length}. " +
                "Formato: TIPO_DOC-NUMERO1-TIPO_UBIC-NUMERO2 (ej: PVE-219836-WAR-3270806)");

        var (docType, num1Str, locType, num2Str) = (parts[0], parts[1], parts[2], parts[3]);

        if (!DocTypeToHex.TryGetValue(docType, out var docHex))
            return EpcEncodeResult.Fail(
                $"Tipo de documento '{docType}' no reconocido. Válidos: {string.Join(", ", DocTypeToHex.Keys)}");

        if (!LocTypeToHex.TryGetValue(locType, out var locHex))
            return EpcEncodeResult.Fail(
                $"Tipo de ubicación '{locType}' no reconocido. Válidos: {string.Join(", ", LocTypeToHex.Keys)}");

        if (!long.TryParse(num1Str, out var num1) || num1 < 0)
            return EpcEncodeResult.Fail($"Número 1 '{num1Str}' no es numérico válido");

        if (!long.TryParse(num2Str, out var num2) || num2 < 0)
            return EpcEncodeResult.Fail($"Número 2 '{num2Str}' no es numérico válido");

        if (num1 > 999_999_999)
            return EpcEncodeResult.Fail($"Número 1 ({num1}) excede máximo (999999999)");

        if (num2 > 999_999_999)
            return EpcEncodeResult.Fail($"Número 2 ({num2}) excede máximo (999999999)");

        var epc = $"{FormatVersion}{docHex}{num1:D9}{locHex}{num2:D9}";
        return EpcEncodeResult.Ok(epc, code);
    }

    /// <summary>
    /// Decodifica un EPC hex de 24 caracteres a código de despacho.
    /// Entrada: "EAAA000219836BB003270806"
    /// Salida:  "PVE-219836-WAR-3270806"
    /// </summary>
    public static EpcDecodeResult Decode(string epcHex)
    {
        if (string.IsNullOrWhiteSpace(epcHex))
            return EpcDecodeResult.Fail("EPC vacío");

        epcHex = epcHex.Trim().ToUpper();

        if (epcHex.Length != 24)
            return EpcDecodeResult.Fail($"EPC debe tener 24 caracteres hex, tiene {epcHex.Length}");

        if (!epcHex.StartsWith("E"))
            return EpcDecodeResult.Fail("EPC no inicia con 'E' — no es un tag Empacor");

        var version = epcHex[..2];
        var prefix1Hex = epcHex[2..4];
        var num1Str = epcHex[4..13];
        var prefix2Hex = epcHex[13..15];
        var num2Str = epcHex[15..24];

        if (!HexToDocType.TryGetValue(prefix1Hex, out var docType))
            return EpcDecodeResult.Fail($"Prefijo de documento '{prefix1Hex}' no reconocido");

        if (!HexToLocType.TryGetValue(prefix2Hex, out var locType))
            return EpcDecodeResult.Fail($"Prefijo de ubicación '{prefix2Hex}' no reconocido");

        if (!long.TryParse(num1Str, out var num1))
            return EpcDecodeResult.Fail($"Número 1 '{num1Str}' no es numérico");

        if (!long.TryParse(num2Str, out var num2))
            return EpcDecodeResult.Fail($"Número 2 '{num2Str}' no es numérico");

        var dispatchCode = $"{docType}-{num1}-{locType}-{num2}";
        return EpcDecodeResult.Ok(dispatchCode, epcHex, version);
    }

    /// <summary>
    /// Normaliza y valida un EPC hexadecimal a exactamente 24 caracteres.
    /// </summary>
    public static string? NormalizeEpc(string epcHex)
    {
        epcHex = epcHex.ToUpper().Replace(" ", "");

        if (!Regex.IsMatch(epcHex, "^[0-9A-F]+$"))
            return null;

        if (epcHex.Length < 24)
            epcHex = epcHex.PadRight(24, '0');
        else if (epcHex.Length > 24)
            epcHex = epcHex[..24];

        return epcHex;
    }
}

// ============================================
// Result types
// ============================================

public record EpcEncodeResult(bool Success, string? EpcHex, string? DispatchCode, string? Error)
{
    public static EpcEncodeResult Ok(string epcHex, string dispatchCode) => new(true, epcHex, dispatchCode, null);
    public static EpcEncodeResult Fail(string error) => new(false, null, null, error);
}

public record EpcDecodeResult(bool Success, string? DispatchCode, string? EpcHex, string? Version, string? Error)
{
    public static EpcDecodeResult Ok(string dispatchCode, string epcHex, string version) => new(true, dispatchCode, epcHex, version, null);
    public static EpcDecodeResult Fail(string error) => new(false, null, null, null, error);
}
