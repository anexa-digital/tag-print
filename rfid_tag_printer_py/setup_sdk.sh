#!/bin/bash
# ============================================
# Setup SDK para RFID Tag Printer Python (WSL)
# ============================================
#
# El SDK UniPRT fue compilado con Python 3.8.
# Este script instala Python 3.8, copia las .so
# y verifica que todo funcione.
#
# Uso:
#   chmod +x setup_sdk.sh
#   ./setup_sdk.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Python requerido por el SDK (compilado con 3.8.10)
REQUIRED_PYTHON="python3.8"

# Ruta al SDK Linux x64
SDK_SOURCE="$PROJECT_ROOT/doc/TSC-UniPRT-SDK_V2/Local/UniPRT_SDK_Python/UniPRT_SDK_Python/Linux/SDK/x64"

# Directorio local para las librerías
SDK_LOCAL="$SCRIPT_DIR/sdk_libs"

echo "============================================"
echo " Setup SDK UniPRT Python para WSL"
echo "============================================"
echo ""

# ---- Paso 1: Verificar/instalar Python 3.8 ----
echo "--- Paso 1: Python 3.8 ---"
echo ""

if command -v $REQUIRED_PYTHON &>/dev/null; then
    PY_VERSION=$($REQUIRED_PYTHON --version 2>&1)
    echo "Python 3.8 encontrado: $PY_VERSION"
else
    echo "Python 3.8 NO encontrado. Instalando..."
    echo ""
    echo "  Se necesita sudo para instalar Python 3.8 desde deadsnakes PPA."
    echo ""
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.8 python3.8-dev python3.8-distutils
    
    if command -v $REQUIRED_PYTHON &>/dev/null; then
        PY_VERSION=$($REQUIRED_PYTHON --version 2>&1)
        echo ""
        echo "Python 3.8 instalado: $PY_VERSION"
    else
        echo ""
        echo "ERROR: No se pudo instalar Python 3.8"
        echo "  Intenta manualmente:"
        echo "    sudo add-apt-repository ppa:deadsnakes/ppa"
        echo "    sudo apt-get update"
        echo "    sudo apt-get install python3.8 python3.8-dev"
        exit 1
    fi
fi
echo ""

# ---- Paso 2: Instalar dependencias ----
echo "--- Paso 2: Dependencias del sistema ---"
echo ""
if dpkg -s libusb-1.0-0 &>/dev/null; then
    echo "libusb-1.0-0 ya instalado."
else
    echo "Instalando libusb..."
    sudo apt-get install -y libusb-1.0-0 libusb-1.0-0-dev
fi

# El SDK requiere pyusb, Pillow y numpy internamente (en los .so de comunicación)
# Dependencias pip requeridas por el SDK (los .so las importan internamente)
# bluetooth se resuelve con un stub local (bluetooth.py), no con pybluez
SDK_PIP_DEPS="pyusb Pillow numpy"
SDK_PIP_MODS="usb    PIL    numpy"
MISSING_DEPS=""

set -- $SDK_PIP_MODS
for dep in $SDK_PIP_DEPS; do
    pymod=$1; shift
    if ! $REQUIRED_PYTHON -c "import $pymod" &>/dev/null; then
        MISSING_DEPS="$MISSING_DEPS $dep"
    fi
done

if [ -z "$MISSING_DEPS" ]; then
    echo "Dependencias Python ya instaladas: $SDK_PIP_DEPS"
else
    echo "Instalando dependencias Python:$MISSING_DEPS"
    if ! $REQUIRED_PYTHON -m pip --version &>/dev/null; then
        echo "  pip no encontrado, instalando..."
        curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | $REQUIRED_PYTHON
    fi
    $REQUIRED_PYTHON -m pip install $MISSING_DEPS
fi
echo "  bluetooth: resuelto con stub local (bluetooth.py)"
echo ""

# ---- Paso 3: Verificar SDK ----
echo "--- Paso 3: SDK UniPRT ---"
echo ""

if [ ! -d "$SDK_SOURCE" ]; then
    echo "ERROR: No se encontró el directorio del SDK:"
    echo "  $SDK_SOURCE"
    echo ""
    echo "Asegúrate de que el repositorio tiene la carpeta doc/ con el SDK."
    exit 1
fi

SO_COUNT=$(ls -1 "$SDK_SOURCE"/*.so 2>/dev/null | wc -l)
echo "SDK encontrado en: $SDK_SOURCE"
echo "Librerías .so encontradas: $SO_COUNT"
echo ""

# ---- Paso 4: Copiar librerías ----
echo "--- Paso 4: Copiar librerías ---"
echo ""

if [ -d "$SDK_LOCAL" ]; then
    echo "Limpiando directorio existente: $SDK_LOCAL"
    rm -rf "$SDK_LOCAL"
fi

mkdir -p "$SDK_LOCAL"

# En WSL, los archivos en /mnt/c/ pueden tener problemas de rendimiento.
# Copiamos las .so al directorio local.
echo "Copiando librerías..."
cp "$SDK_SOURCE"/*.so "$SDK_LOCAL"/
chmod +x "$SDK_LOCAL"/*.so

echo "Copiadas $SO_COUNT librerías a $SDK_LOCAL"
echo ""

# Crear archivo de configuración
cat > "$SCRIPT_DIR/.sdk_path" << EOF
# Generado por setup_sdk.sh - $(date)
UNIPRT_SDK_PATH=$SDK_LOCAL
EOF

# ---- Paso 5: Verificar importación ----
echo "--- Paso 5: Verificar importación ---"
echo ""

cd "$SDK_LOCAL"
$REQUIRED_PYTHON -c "
import sys
sys.path.insert(0, '.')
try:
    import CommSDK
    print('  CommSDK importado correctamente!')
    sdk = CommSDK.CommSDK()
    print('  Instancia CommSDK creada correctamente!')
    print('')
    print('  SDK LISTO!')
except ImportError as e:
    print(f'  ERROR importando CommSDK: {e}')
    print('')
    print('  Si el error menciona libusb:')
    print('    sudo apt-get install libusb-1.0-0 libusb-1.0-0-dev')
    sys.exit(1)
except Exception as e:
    print(f'  CommSDK importado, pero error al instanciar: {e}')
    print('  (Puede ser normal si no hay impresora conectada)')
"

echo ""
echo "============================================"
echo " Setup completado!"
echo "============================================"
echo ""
echo "Para ejecutar la aplicación:"
echo ""
echo "  cd $SCRIPT_DIR"
echo "  $REQUIRED_PYTHON main.py"
echo ""
