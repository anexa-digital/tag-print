"""
Stub module for bluetooth (pybluez).
The SDK imports this internally but we only use Ethernet (TCP/IP).
Provides empty classes/functions so CommSDK loads without error.
"""

# BtComm.so tries to access these
RFCOMM = 3
BTPROTO_RFCOMM = 3


class BluetoothSocket:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Bluetooth not available (stub module)")

    def connect(self, *args):
        pass

    def send(self, *args):
        pass

    def recv(self, *args):
        return b""

    def close(self):
        pass


class BluetoothError(Exception):
    pass


def discover_devices(*args, **kwargs):
    return []


def lookup_name(*args, **kwargs):
    return None
