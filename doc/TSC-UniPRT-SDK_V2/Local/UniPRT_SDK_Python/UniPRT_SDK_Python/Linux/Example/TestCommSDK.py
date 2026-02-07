import CommSDK
import ctypes
import threading
import time
from enum import Enum


TSC_USB_VID = 0x1203
PTX_USB_VID = 0x14ae

Comm_Sdk_Instance = CommSDK.CommSDK()

Connected = False
_bAsyncListening = False
listenerThread = None
currentText = ""
file_path = ""
mutex = threading.Lock()
comboIdx = -1


class BRAND(Enum):
    TSC = 1
    PTX = 2


def ListenerAsync():

    global Connected
    global _bAsyncListening
    global mutex
    global currentText


    while _bAsyncListening and Connected:
    
      time.sleep(0.5) # Sleep for 500 milliseconds
     
      if not _bAsyncListening:
            break

      with mutex:
        iBytes = Comm_Sdk_Instance.GetBytesAvailable()

        
        if not _bAsyncListening:
            break

        
        if iBytes > 0:
            pBuf = (ctypes.c_byte * iBytes)()
            Comm_Sdk_Instance.Read(pBuf, iBytes)

            
            if not _bAsyncListening:
                break

            char_str = ctypes.cast(pBuf, ctypes.c_char_p).value.decode('utf-8', errors='ignore')
            char_str = char_str[:iBytes]
            if (len(char_str)):
                currentText += char_str
                print("Response:")
                print(currentText)
                currentText = ""

        else:
            time.sleep(0.01)  # Sleep for 10 milliseconds

    return





def on_AsyncListen():
    global _bAsyncListening
    global listenerThread
    global Connected
   
    if _bAsyncListening:
        print("---Deactivate Listener")
        _bAsyncListening = False
        Comm_Sdk_Instance.StopAsyncListening()
        
        
        if listenerThread and listenerThread.is_alive():
           listenerThread.join()

    else:
        if not Connected:
            print("Connect first. Can't listen without a valid open/active connection.")
            return

        _bAsyncListening = True

        # Start the async listener thread
        listenerThread = threading.Thread(target=ListenerAsync)
        listenerThread.start()
        time.sleep(1)
    return



class Tuple_c(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("vendorId", ctypes.c_ushort),
                ("productId", ctypes.c_ushort)]


def main():
    # USB Enum
    devices, count = Comm_Sdk_Instance.GetAvailableDevices()
    print("Number of devices:", count)

    usbItemDescList = []
    usb_tuple = Tuple_c()
    TscPrinterIdx = -1
    global _bAsyncListening
    global Connected

    if count > 0:
        for i in range(count):
            print(f"Device {i}: VendorID= 0x{devices[i].vendorId:04X} ProductID= 0x{devices[i].productId:04X}")

            usbItemDesc = ""  # 重置usbItemDesc为空字符串

            if TSC_USB_VID == devices[i].vendorId:
                usbItemDesc = "TSC"
                TscPrinterIdx = i
            elif PTX_USB_VID == devices[i].vendorId:
                usbItemDesc = "Printronix"
                TscPrinterIdx = i

            if usbItemDesc:
                usbItemDesc += f",0x{devices[i].vendorId:X},0x{devices[i].productId:X}"
                usbItemDescList.append(usbItemDesc)
                
                
    
    # USB I/F
    if TscPrinterIdx != -1:
        usb_tuple.vendorId = devices[TscPrinterIdx].vendorId
        usb_tuple.productId = devices[TscPrinterIdx].productId
        Comm_Sdk_Instance.UsbConnection(usb_tuple)
    
    
    


    # NET I/F
    #Comm_Sdk_Instance.TcpConnection("192.168.50.30", 9100)
    #Comm_Sdk_Instance.TcpConnection("fe80::208:96ff:fe40:9b04%ens33", 9100) ## IPv6 Link-Local Address
    #Comm_Sdk_Instance.TcpConnection("2001:b030:2219:c40:208:96ff:fe40:9b04", 9100) ## Global Unicast IPv6 Address
    # BT I/F
    #Comm_Sdk_Instance.BtConnection("44:B7:D0:2E:6E:B7")
    #Comm_Sdk_Instance.BtConnection("00:0C:BF:16:18:D3")

    # COM I/F
    #Comm_Sdk_Instance.ComConnection("/dev/ttyUSB0", 9600)

    Comm_Sdk_Instance.Open()
    if Comm_Sdk_Instance.Connected():
        Connected = True
        content = ""
        
        
        
        #Print job
        content += "SIZE 3,2\r\n"
        content += "GAP 0 mm, 0 mm\r\n"
        content += "DIRECTION 1\r\n"
        content += "CLS\r\n"
        content += "TEXT 10, 30, \"3\", 0, 1, 1, \"123456\"\r\n"
        content += "BARCODE 10, 100, \"EAN13\", 80, 1, 0, 2, 4, \"123456789012\"\r\n"
        content += "TEXT 10, 70, \"4\", 0, 1, 1, \"TEST PRINTOUT\"\r\n"
        content += "PRINT 1, 1\r\n"
        #Print job
        


       

        """
        #Print job
        content += "!PTX_SETUP\r\n"
        content += "PRINTJOB-START;1234\r\n"
        content += "PTX_END\r\n"
        content += "~NORMAL\r\n"
        content += "~CREATE;C39;72\r\n"
        content += "SCALE;DOT\r\n"
        content += "PAGE;30;40\r\n"
        content += "ALPHA\r\n"
        content += "C10;1;37;0;0;@HELLO@\r\n"
        content += "C16;54;37;0;0;@*World*@\r\n"
        content += "STOP\r\n"
        content += "BARCODE\r\n"
        content += "C128C;XRD3:3:6:6:9:9:12:12;H6;10;64\r\n"
        content += "@World@\r\n"
        content += "STOP\r\n"
        content += "END\r\n"
        content += "~EXECUTE;C39\r\n"
        content += "~NORMAL\r\n"
        content += "!PTX_SETUP\r\n"
        content += "PRINTJOB-END;1234\r\n"
        content += "PTX_END\r\n"
        #Print job
        """

        #content += "PAPER ADVANCE 1.0\r\n"
        
        
        
        
        


        
        """
        #AsyncListen
        on_AsyncListen()
        content += "A$=\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\"\r\n"
        content += "OUT A$\r\n"
        #AsyncListen
        """


        
        
        """
        content += "!PTX_SETUP\r\n"
        content += "UPMC\r\n"
        content += "{\r\n" 
        content += "\"Command\": \"Cfg.Item\",\r\n"
        content += "\"From\": \"4023381\",\r\n"
        content += "\"TrackNo\": \"7\",\r\n"
        content += "\"Content\": {\r\n"
        content += "   \"Speed\" : null,\r\n"
        content += "    \"ODV.Symbol\" : null,\r\n"
        content += "   \"Label.Sensor\":null\r\n"     
        content += "}\r\n"
        content += "}\r\n"
        content += "PTX_END\r\n"
        """
        
        
        


        
        print()
        print("Send to Printer:")
        print(content)
        charBuffer = content.encode('utf-8')
        Comm_Sdk_Instance.Write(bytearray(charBuffer), len(charBuffer))
        


        
        """
        # WriteAndWaitForResponse
        content = "FEED 100\r\nOUT \"12345678\"\r\n"
        print()
        print("Send to Printer:")
        print(content)
        Length = len(content)
        Str = Comm_Sdk_Instance.WriteAndWaitForResponse(bytearray(content, 'utf-8'), Length, 1000, 500, "\r\n")
        if(Str):
            Response = Str.decode()
            print()
            print("Response")
            print(Response)
        # WriteAndWaitForResponse
        """
        
       
    
    else:
        print("Failed to Connect Printer")
        return 1
    
    userInput = None

    # 循環等待用戶輸入，直到用戶輸入0為止
    
    while userInput != 0:
        print("\nPress 0 to exit")
        userInput = int(input())
        time.sleep(0.5)

    # 使用者輸入0 後程式結束
    print("\nProgram exit\n")
    
    

    _bAsyncListening = False
    Connected = False
    if Comm_Sdk_Instance.Connected() == True:
          Comm_Sdk_Instance.Close()

    return 0





if __name__ == "__main__":
    main()



