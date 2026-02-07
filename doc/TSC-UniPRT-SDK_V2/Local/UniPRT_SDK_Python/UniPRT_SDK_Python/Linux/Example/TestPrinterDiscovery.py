import Discovery
from enum import Enum
import time

class BRAND_IDX(Enum):
    ALL = 0
    TSC = 1
    PTX = 2

Discovery_Sdk_Instance = Discovery.Discovery()


def main():
    print("Searching for printers...")
    printer_list = Discovery_Sdk_Instance.GetPrinterList(BRAND_IDX.ALL.value, 3000)
    #printer_list = Discovery_Sdk_Instance.GetPrinterList(BRAND_IDX.TSC.value, 3000)
    #printer_list = Discovery_Sdk_Instance.GetPrinterList(BRAND_IDX.PTX.value, 3000)

    if not printer_list:
        print("No Printers found.")
    else:
        print("Printers found at:")
        for ip in printer_list:
            print(ip)


    userInput = None

    # 循環等待用戶輸入，直到用戶輸入0為止
    
    while userInput != 0:
        print("\nPress 0 to exit")
        userInput = int(input())
        time.sleep(0.5)

    # 使用者輸入0 後程式結束
    print("\nProgram exit\n")




if __name__ == "__main__":
    main()