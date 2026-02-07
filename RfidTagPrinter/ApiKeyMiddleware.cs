namespace RfidTagPrinter;

/// <summary>
/// Middleware que valida el header X-Api-Key contra la clave configurada.
/// Excluye /health del check de autenticación.
/// </summary>
public class ApiKeyMiddleware
{
    private const string ApiKeyHeaderName = "X-Api-Key";
    private readonly RequestDelegate _next;
    private readonly string _apiKey;

    public ApiKeyMiddleware(RequestDelegate next, IConfiguration configuration)
    {
        _next = next;
        _apiKey = configuration["API_KEY"] 
            ?? configuration["ApiKey"] 
            ?? throw new InvalidOperationException(
                "API_KEY no configurada. Establece la variable de entorno API_KEY o ApiKey en appsettings.json");
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Excluir /health del check
        if (context.Request.Path.StartsWithSegments("/health"))
        {
            await _next(context);
            return;
        }

        if (!context.Request.Headers.TryGetValue(ApiKeyHeaderName, out var extractedApiKey))
        {
            context.Response.StatusCode = 401;
            await context.Response.WriteAsJsonAsync(new { error = "API key requerida. Envía header X-Api-Key." });
            return;
        }

        if (!string.Equals(extractedApiKey, _apiKey, StringComparison.Ordinal))
        {
            context.Response.StatusCode = 401;
            await context.Response.WriteAsJsonAsync(new { error = "API key inválida." });
            return;
        }

        await _next(context);
    }
}
