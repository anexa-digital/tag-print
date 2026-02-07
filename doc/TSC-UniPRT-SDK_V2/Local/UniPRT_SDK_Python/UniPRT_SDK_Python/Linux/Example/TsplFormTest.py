from enum import Enum
import LabelMakerSDK



class ScaleEnum:
    Dot = 0
    MM = 1
    Inch = 2


class MaxicodeModeEnum:
    MODE_2 = 2
    MODE_3 = 3
    MODE_4 = 4


class Pdf417ErrCorrectionEnum:
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8


class AztecCodeTypeEnum:
    Default = 0
    FixedErrCorrection = 1
    Compact = 2
    Full = 3
    Rune = 4


class RotateEnum:
    _None = 0
    ClockWise = 1
    CounterClockWise = 2
    Inverted = 3


class QRCodeMaskEnum:
    Mask_0 = 0
    Mask_1 = 1
    Mask_2 = 2
    Mask_3 = 3
    Mask_4 = 4
    Mask_5 = 5
    Mask_6 = 6
    Mask_7 = 7
    Mask_8 = 8


class QRCodeManualEncodingEnum:
    Numeric = 0
    AlphaNumeric = 1
    Binary = 2
    Kanji = 3


class QRCodeErrorCorrectionEnum:
    EC_7 = 0
    EC_15 = 1
    EC_25 = 2
    EC_30 = 3


class QRCodeModelEnum:
    MODEL_1 = 0
    MODEL_2 = 1


class RfidMemBlockEnum:
    InvalidMemBlock = 0
    EPC = 1
    TID = 2
    User = 3
    AccessCode = 4
    KillCode = 5
    PC = 6
    Reserve = 7


class RfidPasswordTypeEnum:
    _None = 0
    Lock = 1
    PermaLock = 2
    Unlock = 3
    PermaUnlock = 4


class FontSizeUnitsEnum:
    Ruler = 0
    Points = 1
    Percent = 2


class FontStyleEnum:
    Normal = 0
    Bold = 1
    Italic = 2


class AlignEnum:
    Default = 0
    Left = 1
    Center = 2
    Right = 3


class BarcodeTypeEnum_1D:
    NOT_DEFINED = 0
    Code_93 = 1
    Code_39 = 2
    Code_128 = 3
    EAN13 = 4
    EAN8 = 5
    UPCA = 6
    I2of5 = 7
    CODABAR = 8


TSPL = 0
PGL = 1


class BRAND(Enum):
    TSC = 1
    PTX = 2



class COMM_TYP(Enum):
    USB_COMM = 0
    TCP_COMM = 1
    BT_COMM = 2
    COM_COMM  = 3

NON_USED = -1
Label_Maker_SDK = LabelMakerSDK.LabelMakerSDK()


LabelString = ""

def SimpleTextLabel(LabelString):
    
    Label_Maker_SDK.WindowsFont(30, 0, 0, 0, "arial.ttf", "Test Windows Font", BRAND.TSC.value, "BmpWindowsFont.bmp", COMM_TYP.USB_COMM.value, None, 0, 0, "", 0)
    #Label_Maker_SDK.WindowsFont(30, 0, 0, 0, "NotoSansCJK-Regular.ttc", "測試 Windows Font 功能", BRAND.TSC.value, "BmpWindowsFont.bmp", COMM_TYP.USB_COMM.value, None, 0, 0, "", 0)
    #Label_Maker_SDK.WindowsFont(30, 0, 0, 0, "NotoSansCJK-Regular.ttc", "測試繁體中文功能", BRAND.TSC.value, "BmpWindowsFont.bmp", COMM_TYP.USB_COMM.value, None, 0, 0, "", 0)

    #Label_Maker_SDK.WindowsFont(20, 0, 0, 0, "arial.ttf", "Test Windows Font", BRAND.PTX.value, "BmpWindowsFont", COMM_TYP.USB_COMM.value, None, 0, 0, "", 0)
    #Label_Maker_SDK.WindowsFont(20, 0, 0, 0, "NotoSansCJK-Regular.ttc", "測試 Windows Font 功能", BRAND.PTX.value, "BmpWindowsFont", COMM_TYP.USB_COMM.value, None, 0, 0, "", 0)
    #Label_Maker_SDK.WindowsFont(20, 0, 0, 0, "NotoSansCJK-Regular.ttc", "測試繁體中文功能", BRAND.PTX.value, "BmpWindowsFont", COMM_TYP.USB_COMM.value, None, 0, 0, "", 0)
    #Label_Maker_SDK.WindowsFont(20, 0, 0, 0, "arial.ttf", "Test Windows Font", BRAND.PTX.value, "BmpWindowsFont", COMM_TYP.USB_COMM.value, None, 0, 0, "", 0)
    


    Label_Maker_SDK.CreateLabel(TSPL, "SimpleLabel", 300, ScaleEnum.Inch)
    #Label_Maker_SDK.CreateLabel(PGL, "SimpleLabel", 300, ScaleEnum.Inch)

    
    Label_Maker_SDK.CreateLines(2.5, 1 / 16, 2.5, 1.0, 1 / 32, ScaleEnum.Inch)
    Label_Maker_SDK.CreateLines(0.12, 1.0, 3.88, 1.0, 1 / 32, ScaleEnum.Inch)
    Label_Maker_SDK.CreateLines(0.12, 3.5, 3.88, 3.5, 1 / 32, ScaleEnum.Inch)
    Label_Maker_SDK.CreateBoxs(0.5, 1.25, 3.5, 2.25, 1 / 16, ScaleEnum.Inch)
    

    
    # Text
    Label_Maker_SDK.CreateTexts(2.0, 1.25 + 7 / 16, 3 / 16, 7 / 16, "MY MAGIC", ScaleEnum.Inch, FontSizeUnitsEnum.Ruler,
                    NON_USED, AlignEnum.Center, "93952.sf", RotateEnum._None)
    Label_Maker_SDK.CreateTexts(2.0, 1.25 + 1.0 - 3 / 16, 3 / 16, 7 / 16, "PRODUCT", ScaleEnum.Inch, FontSizeUnitsEnum.Ruler,
                    NON_USED, AlignEnum.Center, "93952.sf", RotateEnum._None)

    Label_Maker_SDK.CreateTexts(5.0, 5.0, 2.5, 5.0, "TO:", ScaleEnum.MM, FontSizeUnitsEnum.Ruler,
                    FontStyleEnum.Bold, AlignEnum.Default, "92248.sf", RotateEnum._None)
    Label_Maker_SDK.CreateTexts((2.5 + 1 / 16) * 25.4, 5.0, 2.5, 5.0, "FROM:", ScaleEnum.MM, FontSizeUnitsEnum.Ruler,
                    FontStyleEnum.Bold, AlignEnum.Default, "92248.sf", RotateEnum._None)

    Label_Maker_SDK.CreateTexts((2.5 + 1 / 16 + 1 / 8) * 25.4, 17.0, 2.0, 3.0, "Happy Inc.", ScaleEnum.MM, FontSizeUnitsEnum.Percent,
                    FontStyleEnum.Italic, AlignEnum.Default, "92500.sf", RotateEnum._None)
    
    Label_Maker_SDK.Picture(100, 200, "BmpWindowsFont.bmp") # TSC
    #Label_Maker_SDK.Picture(5, 1, "BmpWindowsFont") # PTX

    LabelString = Label_Maker_SDK.LabelToString(LabelString)
    return LabelString



def BcdMaxicodes(LabelString):
    
    _MaxicodeMsgStructured = 0
    _MaxicodeMsgStructuredOpenSystemStandard = 1
    _MaxicodeMsg = 2

    Label_Maker_SDK.CreateLabel(TSPL, "MaxiBcds", 300, ScaleEnum.Inch)
    #Label_Maker_SDK.CreateLabel(PGL, "MaxiBcds", 300, ScaleEnum.Inch)
    Label_Maker_SDK.CreateMaxicodeBarcodes(_MaxicodeMsgStructured, MaxicodeModeEnum.MODE_2, "902557317", "800", "200", "Maxicode Carrier Standard", "", "", 0.5, 0.5, ScaleEnum.Inch, False, RotateEnum._None)
    Label_Maker_SDK.CreateMaxicodeBarcodes(_MaxicodeMsg, MaxicodeModeEnum.MODE_4, "", "", "", "Maxicode unstructured", "", "123456789", 0.5, 3.5, ScaleEnum.Inch, False, RotateEnum._None)
    LabelString = Label_Maker_SDK.LabelToString(LabelString)
    return LabelString



def BcdAztec(LabelString):
    
    #Label_Maker_SDK.CreateLabel(TSPL, "AztecBcodes", 300, ScaleEnum.Inch)
    Label_Maker_SDK.CreateLabel(PGL, "AztecBcodes", 300, ScaleEnum.Inch)
    Label_Maker_SDK.CreateAztecBarcodes(0.25, 1.0, "Mr. AirTraveler, seat A, flight 200", ScaleEnum.Inch, 0.025, AztecCodeTypeEnum.Default, NON_USED, NON_USED, RotateEnum._None)
    Label_Maker_SDK.CreateAztecBarcodes(1.5, 1.0, "Mr. AirTraveler, seat A, flight 200", ScaleEnum.Inch, 0.025, AztecCodeTypeEnum.FixedErrCorrection, 30, NON_USED, RotateEnum._None)
    Label_Maker_SDK.CreateAztecBarcodes(0.25, 2.25, "Mr. AirTraveler, seat A, flight 200", ScaleEnum.Inch, 0.025, AztecCodeTypeEnum.Compact, NON_USED, 4, RotateEnum._None)
    Label_Maker_SDK.CreateAztecBarcodes(0.75, 4.0, "255", ScaleEnum.Inch, 0.025, AztecCodeTypeEnum.Rune, NON_USED, NON_USED, RotateEnum._None)
    LabelString = Label_Maker_SDK.LabelToString(LabelString)
    return LabelString



def BcdQRCode(LabelString):
    
    enText = "Tree in the forest"
    jaText = "森の中の木"
    dataManuallyEncoded = None

    Label_Maker_SDK.CreateLabel(TSPL, "QRBcodes", 300, ScaleEnum.Inch)
    #Label_Maker_SDK.CreateLabel(PGL, "QRBcodes", 300, ScaleEnum.Inch)
    Label_Maker_SDK.CreateQRBarcodes(0.25, 1.0, enText, ScaleEnum.Inch, 0.025, NON_USED, dataManuallyEncoded,
                        NON_USED, NON_USED, RotateEnum._None)
    Label_Maker_SDK.CreateQRBarcodes(1.5, 1.0, enText, ScaleEnum.Inch, 0.025, QRCodeMaskEnum.Mask_4, dataManuallyEncoded,
                        NON_USED, NON_USED, RotateEnum._None)

    if dataManuallyEncoded is None:
        dataManuallyEncoded = [
            (QRCodeManualEncodingEnum.Numeric, "12345678"),
            (QRCodeManualEncodingEnum.AlphaNumeric, " TREE IN THE FOREST "),
            (QRCodeManualEncodingEnum.AlphaNumeric, "森の中の木")
        ]

        Label_Maker_SDK.CreateQRBarcodes(1.75, 3.75, "", ScaleEnum.Inch, 0.025, QRCodeMaskEnum.Mask_4, dataManuallyEncoded,
                            NON_USED, NON_USED, RotateEnum._None)
    LabelString = Label_Maker_SDK.LabelToString(LabelString)
    return LabelString




def RfidEncode(LabelString):
    
    #Label_Maker_SDK.CreateLabel(PGL, "RfidLbl", 300, ScaleEnum.Inch)
    Label_Maker_SDK.CreateLabel(TSPL, "RfidLbl", 300, ScaleEnum.Inch)

    a32BitField = 0x11223344
    a16BitField = 0xBEEF
    a6CharAsciiString = "MyData"

    Label_Maker_SDK.CreateRfidEncode(a32BitField, a16BitField, a6CharAsciiString, RfidMemBlockEnum.EPC, 0,
                        "", "", RfidPasswordTypeEnum._None, "")
    Label_Maker_SDK.CreateRfidEncode(a32BitField, a16BitField, a6CharAsciiString, RfidMemBlockEnum.User, 2,
                        "MyUserData", "0ABCDE0F", RfidPasswordTypeEnum._None, "")

    LabelString = Label_Maker_SDK.LabelToString(LabelString)
    return LabelString




def BcdPdf417(LabelString):
   
    #Label_Maker_SDK.CreateLabel(PGL, "Pdf417Bcodes", 300, ScaleEnum.Inch)
    Label_Maker_SDK.CreateLabel(TSPL, "Pdf417Bcodes", 300, ScaleEnum.Inch)

    someText = "The happiness in your life depends on the quality of your thoughts. --Marcus Aurelius"
    someShortText = "PI = 3.1415"
    Label_Maker_SDK.CreatePdf417Bcodes(0.25, 0.5, someText, ScaleEnum.Inch, 0.015, 0.05, NON_USED, NON_USED, NON_USED, RotateEnum._None)
    Label_Maker_SDK.CreatePdf417Bcodes(0.25, 1.5, someShortText, ScaleEnum.Inch, 0.015, 0.05, Pdf417ErrCorrectionEnum.LEVEL_0, NON_USED, NON_USED, RotateEnum._None)
    Label_Maker_SDK.CreatePdf417Bcodes(0.25, 2.0, someShortText, ScaleEnum.Inch, 0.015, 0.05, Pdf417ErrCorrectionEnum.LEVEL_5, NON_USED, NON_USED, RotateEnum._None)
    Label_Maker_SDK.CreatePdf417Bcodes(0.25, 3.0, someShortText, ScaleEnum.Inch, 0.015, 0.05, NON_USED, 15, NON_USED, RotateEnum._None)
    Label_Maker_SDK.CreatePdf417Bcodes(0.25, 4.0, someShortText, ScaleEnum.Inch, 0.015, 0.05, NON_USED, NON_USED, 5, RotateEnum._None)

    LabelString = Label_Maker_SDK.LabelToString(LabelString)
    return LabelString




def BcdDataMatrix(LabelString):
    
    Label_Maker_SDK.CreateLabel(TSPL, "DMatrixBcds", 200, ScaleEnum.Inch)
    #Label_Maker_SDK.CreateLabel(PGL, "DMatrixBcds", 300, ScaleEnum.Inch)
    Label_Maker_SDK.CreateDataMatrixBarcodes(0.25, 0.25, "Default DataMatrix", ScaleEnum.Inch, NON_USED, RotateEnum._None, False, "", 0, 0, 0, 0)
    Label_Maker_SDK.CreateDataMatrixBarcodes(1.25, 0.25, "Rectangular DataMatrix", ScaleEnum.Inch, 0.025, RotateEnum.CounterClockWise, True, "", 0, 0, 0, 0)
    Label_Maker_SDK.CreateDataMatrixBarcodes(2.25, 0.25, "Line 1 DataMatrix", ScaleEnum.Inch, NON_USED, RotateEnum._None, False, "Line 2 content/r/nLine 3 content", 0x0D, 0x0A, 0, 0)
    Label_Maker_SDK.CreateDataMatrixBarcodes(1.25, 1.75, "DataMatrix with user defined dimensions", ScaleEnum.Inch, 0.03, RotateEnum._None, True, "", 0, 0, 16, 36)

    LabelString = Label_Maker_SDK.LabelToString(LabelString)
    return LabelString




def Barcode1D(LabelString):
    
    Label_Maker_SDK.CreateLabel(TSPL, "Barcode1D", 300, ScaleEnum.Inch)
    #Label_Maker_SDK.CreateLabel(PGL, "Barcode1D", 300, ScaleEnum.Inch)
    Label_Maker_SDK.CreateBarcode1D(0.5, 1.0 + 1.5 + 1 / 4 + 1.2, "Code 128", ScaleEnum.Inch, 0.015, 0.015 * 4.1, 1.2, BarcodeTypeEnum_1D.Code_128, True, RotateEnum._None, False)
    Label_Maker_SDK.CreateBarcode1D(0.5, 3.5 - 1 / 8 - 0.6, "CODE 93", ScaleEnum.Inch, 0.025, 0.025 * 4.1, 0.6, BarcodeTypeEnum_1D.Code_93, True, RotateEnum._None, False)

    LabelString = Label_Maker_SDK.LabelToString(LabelString)
    return LabelString





def main():
    LabelString = ""

    LabelString = SimpleTextLabel(LabelString)
    #LabelString = BcdMaxicodes(LabelString)
    #LabelString = BcdAztec(LabelString)
    #LabelString = BcdQRCode(LabelString)
    #LabelString = RfidEncode(LabelString)
    #LabelString = BcdPdf417(LabelString)
    #LabelString = BcdDataMatrix(LabelString)
    #LabelString = Barcode1D(LabelString)

    if LabelString:
        print(LabelString)

    Label_Maker_SDK.CloseLabel()
    LabelString = ""

    return 0


if __name__ == "__main__":
    main()