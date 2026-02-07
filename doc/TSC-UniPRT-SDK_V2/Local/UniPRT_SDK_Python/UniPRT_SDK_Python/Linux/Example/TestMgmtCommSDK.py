import CommSDK
import ctypes
import threading
import time
import JsonSDK
from JsonSDK import COMM_TYP
from ctypes import c_char_p
import pprint


TSC_USB_VID = 0x1203
PTX_USB_VID = 0x14ae

Comm_Sdk_Instance = CommSDK.CommSDK()
Json_Sdk_Instance = JsonSDK.JsonSDK()

Connected = False
_bAsyncListening = False
listenerThread = None
currentText = ""
file_path = ""
mutex = threading.Lock()
comboIdx = -1


def ListenerAsync():

    global currentText
    global Connected
    global _bAsyncListening
    global mutex
    while _bAsyncListening and Connected:
        time.sleep(0.5)

        # 檢查 _bAsyncListening 狀態
        if not _bAsyncListening:
            break

        with mutex:
            i_unread_msg_count = Json_Sdk_Instance.MessengerUnreadMsgCount()


            # 檢查 _bAsyncListening 狀態
            if not _bAsyncListening:
                break
            
            if i_unread_msg_count > 0:
                str_next_msg = (c_char_p * 1)()  # 創建一個指針陣列，用於存放 c_char_p 物件
                Json_Sdk_Instance.MessengerReadNextMsg(str_next_msg)

                # 檢查 _bAsyncListening 狀態
                if not _bAsyncListening:
                    break
                
                if str_next_msg[0] == b'':
                    continue    

                
                if str_next_msg[0] is not None:
                    currentText = str_next_msg[0].decode('utf-8')
                    print(currentText)
                    currentText = ""
                    
            else:
                time.sleep(0.01)  # C# delay 200 ms





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
    

class CObject(ctypes.Structure):
    pass

MAX_INPUT_MSG_CAPACITY = 20
MAX_WAIT_TIME_SECS = 5



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

            if usbItemDesc:
                usbItemDesc += f",0x{devices[i].vendorId:X},0x{devices[i].productId:X}"
                usbItemDescList.append(usbItemDesc)
                
    
    
    
    # USB I/F
    """
    if TscPrinterIdx != -1:
        usb_tuple.vendorId = devices[TscPrinterIdx].vendorId
        usb_tuple.productId = devices[TscPrinterIdx].productId
        Comm_Sdk_Instance.UsbConnection(usb_tuple)
    """
    
    
    
    
    # NET I/F
    Comm_Sdk_Instance.TcpConnection("10.0.10.171", 3007)


    # BT I/F
    #Comm_Sdk_Instance.BtConnection("44:B7:D0:2E:6E:B7")
    #Comm_Sdk_Instance.BtConnection("00:0C:BF:16:18:D3")
    #Comm_Sdk_Instance.BtConnection("00:0C:BF:12:15:FC")



    # COM I/F
    #Comm_Sdk_Instance.ComConnection("/dev/ttyUSB0", 9600)

    

    Comm_Sdk_Instance.Open()
    if Comm_Sdk_Instance.Connected():
        Connected = True
        comm_ptr = CObject()
        comm_ptr = Comm_Sdk_Instance.GetComm()
        Json_Sdk_Instance.MessengerGet(comm_ptr, COMM_TYP.TCP_COMM, MAX_INPUT_MSG_CAPACITY, False)
        #Json_Sdk_Instance.MessengerGet(comm_ptr, COMM_TYP.USB_COMM, MAX_INPUT_MSG_CAPACITY, True)
        #Json_Sdk_Instance.MessengerGet(comm_ptr, COMM_TYP.BT_COMM, MAX_INPUT_MSG_CAPACITY, True)
        #Json_Sdk_Instance.MessengerGet(comm_ptr, COMM_TYP.COM_COMM, MAX_INPUT_MSG_CAPACITY, True)

        
        
        on_AsyncListen()




        print()
        print("Send to Printer:")

        CmdBuffer = "Cfg.Item"
        #CmdBuffer = "Cfg.Prop"
        content = ""
        content += "{\r\n"
        content += "\"Speed\" : null,\r\n"
        #content += "\"ODV.Symbol\" : null,\r\n"
        content += "\"Label.Sensor\":null\r\n"
        content += "}\r\n"
       

        print(content)
        ContentBuffer = content.encode('utf-8')
        _bAsyncListening = False
        if _bAsyncListening:
            Json_Sdk_Instance.MessengerSendMsg(CmdBuffer, content)
            
        else:
            
            global currentText
            time.sleep(1)
            str_response = (c_char_p * 1)()  # 創建一個指針陣列，用於存放 c_char_p 物件
            Json_Sdk_Instance.MessengerSendMsgAndWaitForResponse(CmdBuffer, content, MAX_WAIT_TIME_SECS, str_response)
           
            if str_response[0] is not None:
                currentText += str_response[0].decode('utf-8')
                print(currentText)
                currentText = ""
            



        
        
            """
            #AllValues = Json_Sdk_Instance.GetPrinterAllValues(comm_ptr, COMM_TYP.TCP_COMM, False)
            #AllValues = Json_Sdk_Instance.GetPrinterAllValues(comm_ptr, COMM_TYP.USB_COMM, True)
            #AllValues = Json_Sdk_Instance.GetPrinterAllValues(comm_ptr, COMM_TYP.BT_COMM, True)
            AllValues = Json_Sdk_Instance.GetPrinterAllValues(comm_ptr, COMM_TYP.COM_COMM, True)
            print(AllValues)
            """
            
        



            """
            key = "Ethernet.MAC"
            #Value = Json_Sdk_Instance.GetPrinterValue(comm_ptr, COMM_TYP.TCP_COMM, False, key)
            #Value = Json_Sdk_Instance.GetPrinterValue(comm_ptr, COMM_TYP.USB_COMM, True, key)
            #Value = Json_Sdk_Instance.GetPrinterValue(comm_ptr, COMM_TYP.BT_COMM, True, key)
            Value = Json_Sdk_Instance.GetPrinterValue(comm_ptr, COMM_TYP.COM_COMM, True, key)
            print(Value)
            """
            

            
            """
            keys = ["Ethernet.IP", "Ethernet.MAC", "Ethernet.Speed"]
            #values = Json_Sdk_Instance.GetPrinterValues(comm_ptr, COMM_TYP.TCP_COMM, False, keys)
            #values = Json_Sdk_Instance.GetPrinterValues(comm_ptr, COMM_TYP.USB_COMM, True, keys)
            #values = Json_Sdk_Instance.GetPrinterValues(comm_ptr, COMM_TYP.BT_COMM, True, keys)
            values = Json_Sdk_Instance.GetPrinterValues(comm_ptr, COMM_TYP.COM_COMM, True, keys)
            print(values)
            """

            """
            key = "Ethernet.Speed"
            value = "eAutomatic"
            #result = Json_Sdk_Instance.SetPrinterValue(comm_ptr, COMM_TYP.TCP_COMM, False, key, value)
            #result = Json_Sdk_Instance.SetPrinterValue(comm_ptr, COMM_TYP.USB_COMM, True, key, value)
            #result = Json_Sdk_Instance.SetPrinterValue(comm_ptr, COMM_TYP.BT_COMM, True, key, value)
            result = Json_Sdk_Instance.SetPrinterValue(comm_ptr, COMM_TYP.COM_COMM, True, key, value)
            if result:
                print(f"Successfully set {key} to {value}")
            else:
                print(f"Failed to set {key}")
            """



            """
            key_values = {
                "Ethernet.Speed": "eAutomatic",
                "Image.Width-in": "3.5"
            }
            #result = Json_Sdk_Instance.SetPrinterValues(comm_ptr, COMM_TYP.TCP_COMM, False, key_values)
            #result = Json_Sdk_Instance.SetPrinterValues(comm_ptr, COMM_TYP.USB_COMM, True, key_values)
            #result = Json_Sdk_Instance.SetPrinterValues(comm_ptr, COMM_TYP.BT_COMM, True, key_values)
            result = Json_Sdk_Instance.SetPrinterValues(comm_ptr, COMM_TYP.COM_COMM, True, key_values)
            if result:
                print("Successfully set values.")
            else:
                print("Failed to set values.")
            """





            """
            #key_ = "Speed.Print-mmps"
            key_ = "BT.PairMethod"
            #properties = Json_Sdk_Instance.GetPrinterProperties(comm_ptr, COMM_TYP.TCP_COMM, False, key_)
            #properties = Json_Sdk_Instance.GetPrinterProperties(comm_ptr, COMM_TYP.USB_COMM, True, key_)
            #properties = Json_Sdk_Instance.GetPrinterProperties(comm_ptr, COMM_TYP.BT_COMM, True, key_)
            properties = Json_Sdk_Instance.GetPrinterProperties(comm_ptr, COMM_TYP.COM_COMM, True, key_)
            print(properties)
            """
            
            



            """
            keys = ["Speed", "Label.Sensor"]
            #properties = Json_Sdk_Instance.GetPrinterPropertiesEx(comm_ptr, COMM_TYP.TCP_COMM, False, keys)
            #properties = Json_Sdk_Instance.GetPrinterPropertiesEx(comm_ptr, COMM_TYP.USB_COMM, True, keys)
            #properties = Json_Sdk_Instance.GetPrinterPropertiesEx(comm_ptr, COMM_TYP.BT_COMM, True, keys)
            properties = Json_Sdk_Instance.GetPrinterPropertiesEx(comm_ptr, COMM_TYP.COM_COMM, True, keys)
            print(properties)
            """
            



            
            """
            #AllProperties = Json_Sdk_Instance.GetPrinterAllProperties(comm_ptr, COMM_TYP.TCP_COMM, False)
            #AllProperties = Json_Sdk_Instance.GetPrinterAllProperties(comm_ptr, COMM_TYP.USB_COMM, True)
            #AllProperties = Json_Sdk_Instance.GetPrinterAllProperties(comm_ptr, COMM_TYP.BT_COMM, True)
            AllProperties = Json_Sdk_Instance.GetPrinterAllProperties(comm_ptr, COMM_TYP.COM_COMM, True)
            pprint.pprint(AllProperties)
            """
            
            
            


            

            """
            #Config = Json_Sdk_Instance.GetPrinterConfig(comm_ptr, COMM_TYP.TCP_COMM, False, 1)
            #Config = Json_Sdk_Instance.GetPrinterConfig(comm_ptr, COMM_TYP.USB_COMM, True,1)
            #Config = Json_Sdk_Instance.GetPrinterConfig(comm_ptr, COMM_TYP.BT_COMM, True,1)
            Config = Json_Sdk_Instance.GetPrinterConfig(comm_ptr, COMM_TYP.COM_COMM, True,1)
            with open('output_config.txt', 'w') as file:
                file.write(str(Config))
            #result = Json_Sdk_Instance.SetPrinterConfig(comm_ptr, COMM_TYP.TCP_COMM, False, Config)
            #result = Json_Sdk_Instance.SetPrinterConfig(comm_ptr, COMM_TYP.USB_COMM, True, Config)
            #result = Json_Sdk_Instance.SetPrinterConfig(comm_ptr, COMM_TYP.BT_COMM, True, Config)
            result = Json_Sdk_Instance.SetPrinterConfig(comm_ptr, COMM_TYP.COM_COMM, True, Config)
            if result:
                print(f"Successfully set")
            else:
                print(f"Failed to set")
            """
            
            
            




            
            #AllConfig = Json_Sdk_Instance.GetPrinterAllConfig(comm_ptr, COMM_TYP.TCP_COMM, False)
            #AllConfig = Json_Sdk_Instance.GetPrinterAllConfig(comm_ptr, COMM_TYP.USB_COMM, True)
            #AllConfig = Json_Sdk_Instance.GetPrinterAllConfig(comm_ptr, COMM_TYP.BT_COMM, True)
            AllConfig = Json_Sdk_Instance.GetPrinterAllConfig(comm_ptr, COMM_TYP.COM_COMM, True)
            with open('output_allconfig.txt', 'w') as file:
                file.write(str(AllConfig))
            
            





        
        
        
        
        
        


    
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
          Json_Sdk_Instance.MessengerRelease()
          Comm_Sdk_Instance.Close()
          

    return 0





if __name__ == "__main__":
    main()



