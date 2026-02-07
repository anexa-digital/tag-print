# ============================================
# RFID Tag Printer - Printronix T820
# Multi-stage Docker build
# ============================================

# --- Stage 1: Build ---
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copiar el .nupkg local y nuget.config primero (cache de NuGet restore)
COPY RfidTagPrinter/UniPRT.Sdk.2.0.0.3.nupkg RfidTagPrinter/
COPY RfidTagPrinter/nuget.config RfidTagPrinter/
COPY RfidTagPrinter/RfidTagPrinter.csproj RfidTagPrinter/

# Restore
WORKDIR /src/RfidTagPrinter
RUN dotnet restore

# Copiar el resto del código y compilar
WORKDIR /src
COPY RfidTagPrinter/ RfidTagPrinter/

WORKDIR /src/RfidTagPrinter
RUN dotnet publish -c Release -o /app/publish --no-restore

# --- Stage 2: Runtime ---
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

COPY --from=build /app/publish .

# Puerto de la API
ENV ASPNETCORE_URLS=http://+:5000
EXPOSE 5000

# Variables de entorno con defaults
ENV PRINTER_IP=192.168.3.38
ENV PRINTER_PORT=9100
# API_KEY debe ser proporcionada al correr el contenedor

ENTRYPOINT ["dotnet", "RfidTagPrinter.dll"]
