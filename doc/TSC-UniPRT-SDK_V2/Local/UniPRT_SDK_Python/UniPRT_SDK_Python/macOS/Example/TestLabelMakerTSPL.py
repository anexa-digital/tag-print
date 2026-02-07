from UniPRT.LabelMaker.Interfaces.RfidConvert import RfidConvert
from UniPRT.LabelMaker.TSPL.RfidWrite import RfidWrite
from UniPRT.LabelMaker.TSPL.Label import Label
from UniPRT.LabelMaker.TSPL.Shapes import Line, Box
from UniPRT.LabelMaker.TSPL.BcdMaxicode import (
    MaxicodeMsgStructured,
    MaxicodeBarcode,
    MaxicodeMsg,
    MaxicodeModeEnum,
)
from UniPRT.LabelMaker.TSPL.BcdDataMatrix import DataMatrixBarcode
from UniPRT.LabelMaker.TSPL.BcdAztec import AztecBarcode, AztecCodeTypeEnum
from UniPRT.LabelMaker.Interfaces.Defaults import Defaults
from UniPRT.LabelMaker.Interfaces.Coordinate import (
    Ruler,
    ScaleEnum,
    PrintResolution,
    Points,
)
from UniPRT.LabelMaker.TSPL.Pdf417Barcode import Pdf417Barcode
from UniPRT.LabelMaker.Interfaces.IBcdPdf417 import Pdf417ErrCorrectionEnum
from UniPRT.LabelMaker.Interfaces.IBarcode2D import CellRect, CellSquare
from UniPRT.LabelMaker.Interfaces.IBarcode1D import BarcodeItem
from UniPRT.LabelMaker.TSPL.Barcode1D import Barcode1D, BarcodeTypeEnum1D, BarWidths
from UniPRT.LabelMaker.TSPL.QRBarcode import QRBarcode, QRCodeManualEncodingEnum
from UniPRT.LabelMaker.Interfaces.IRfid import RfidMemBlockEnum
from UniPRT.LabelMaker.Interfaces.IBcdQRCode import QRCodeMaskEnum
from UniPRT.LabelMaker.Interfaces.ISettings import RotateEnum

from UniPRT.LabelMaker.TSPL.TsplPicture import TsplPicture
from UniPRT.LabelMaker.TsplLib.Utilities import TsplWindowsFontWithImageName
from pathlib import Path


def tspl_picture():
    lbl = Label(name="TsplPictureTest")

    Defaults.set_printer_resolution(PrintResolution(dots_per_unit=200, unit=ScaleEnum.INCH))
    Defaults.set_ruler(Ruler(scale=ScaleEnum.INCH))

    picture = TsplPicture(start=Points(x=0.25, y=0.25), image_name="qwe")
    lbl.add_object(picture)

    font_data = TsplWindowsFontWithImageName(
        image_name="qwe",
        font_size=72,
        rotation=0,
        font_style=0,
        font_family_name="Arial",
        content="TestString"
    )
    
    file_path = Path.home() / "Documents" / "wfpgl.txt"
    try:
        file_path.write_bytes(font_data)
        print(f"✅ Font data written to: {file_path}")
    except Exception as e:
        print(f"❌ Failed to write font data: {e}")

    return lbl

def bcd_pdf417():
    lbl = Label(name="Pdf417Bcodes")

    Defaults.set_printer_resolution(
        PrintResolution(dots_per_unit=300, unit=ScaleEnum.INCH)
    )
    Defaults.set_ruler(Ruler(scale=ScaleEnum.INCH))

    some_text = "The happiness in your life depends on the quality of your thoughts. --Marcus Aurelius"
    some_short_text = "PI = 3.1415"

    bcd_default = Pdf417Barcode(start=Points(x=0.25, y=0.50), data=some_text)
    bcd_default.cell_size = CellRect(
        xdim=0.015, ydim=0.050, ruler=Ruler(scale=ScaleEnum.INCH)
    )

    bcd_err_correction_lvl0 = Pdf417Barcode(
        start=Points(x=0.25, y=1.50), data=some_short_text
    )
    bcd_err_correction_lvl0.cell_size = CellRect(
        xdim=0.015, ydim=0.050, ruler=Ruler(scale=ScaleEnum.INCH)
    )
    bcd_err_correction_lvl0.error_correction = Pdf417ErrCorrectionEnum.LEVEL0

    bcd_err_correction_lvl5 = Pdf417Barcode(
        start=Points(x=0.25, y=2.00), data=some_short_text
    )
    bcd_err_correction_lvl5.cell_size = CellRect(
        xdim=0.015, ydim=0.050, ruler=Ruler(scale=ScaleEnum.INCH)
    )
    bcd_err_correction_lvl5.error_correction = Pdf417ErrCorrectionEnum.LEVEL5

    bcd_rows_limited = Pdf417Barcode(start=Points(x=0.25, y=3.00), data=some_short_text)
    bcd_rows_limited.cell_size = CellRect(
        xdim=0.015, ydim=0.050, ruler=Ruler(scale=ScaleEnum.INCH)
    )
    bcd_rows_limited.rows = 15

    bcd_cols_limited = Pdf417Barcode(start=Points(x=0.25, y=4.00), data=some_short_text)
    bcd_cols_limited.cell_size = CellRect(
        xdim=0.015, ydim=0.050, ruler=Ruler(scale=ScaleEnum.INCH)
    )
    bcd_cols_limited.columns = 5

    lbl.add_object(bcd_default)
    lbl.add_object(bcd_err_correction_lvl0)
    lbl.add_object(bcd_err_correction_lvl5)
    lbl.add_object(bcd_rows_limited)
    lbl.add_object(bcd_cols_limited)

    return lbl


def simple_text_label(name, address):
    Defaults.set_printer_resolution(
        PrintResolution(dots_per_unit=600, unit=ScaleEnum.INCH)
    )

    lbl = Label(name="SimpleLabel")

    inch_ruler = Ruler(scale=ScaleEnum.INCH)

    line1 = Line(
        start=Points(x=2.5, y=1.0 / 16.0),
        end=Points(x=2.5, y=1.0),
        line_thickness=1.0 / 32.0,
    )
    line1.ruler = inch_ruler
    lbl.add_object(line1)

    line2 = Line(
        start=Points(x=0.12, y=1.0),
        end=Points(x=3.88, y=1.0),
        line_thickness=1.0 / 32.0,
    )
    line2.ruler = inch_ruler
    lbl.add_object(line2)

    line3 = Line(
        start=Points(x=0.12, y=3.5),
        end=Points(x=3.88, y=3.5),
        line_thickness=1.0 / 32.0,
    )
    line3.ruler = inch_ruler
    lbl.add_object(line3)

    line4 = Box(
        start=Points(x=0.5, y=1.25),
        end=Points(x=3.5, y=2.25),
        line_thickness=1.0 / 16.0,
    )
    line4.ruler = inch_ruler
    lbl.add_object(line4)

    barcode_item_128 = BarcodeItem(
        start=Points(x=0.5, y=(1.0 + 1.5 + 1.0 / 4.0 + 1.2)),
        height=1.2,
        data="Code 128",
    )

    bcd_128 = Barcode1D(barcode=barcode_item_128)
    bcd_128.barcode_type = BarcodeTypeEnum1D.CODE128
    bcd_128.print_human_readable = True
    bcd_128.rotation = RotateEnum.NONE
    bcd_128.ruler = inch_ruler
    bcd_128.bar_widths = BarWidths(narrow_bar=0.015, wide_bar=0.015)
    bcd_128.bar_widths.ruler = Ruler(scale=ScaleEnum.INCH)
    lbl.add_object(bcd_128)

    barcode_item_93 = BarcodeItem(
        start=Points(x=0.5, y=3.5 - 1.0 / 8.0 - 0.6), height=0.6, data="CODE 93"
    )

    bcd_93 = Barcode1D(barcode=barcode_item_93)
    bcd_93.barcode_type = BarcodeTypeEnum1D.CODE93
    bcd_93.print_human_readable = True
    bcd_93.rotation = RotateEnum.NONE
    bcd_93.ruler = inch_ruler
    bcd_93.bar_widths = BarWidths(narrow_bar=0.025, wide_bar=0.025 * 3)
    bcd_93.bar_widths.ruler = Ruler(scale=ScaleEnum.INCH)
    lbl.add_object(bcd_93)

    return lbl


def rfid_encode():
    lbl = Label(name="RfidLbl")

    a32_bit_field = 0x11223344
    a16_bit_field = 0xBEEF
    a6_char_ascii_string = "MyData"
    epc_hex_data = RfidConvert.to_hex_from_bytes(a32_bit_field)
    epc_hex_data += RfidConvert.to_hex_from_bytes(a6_char_ascii_string.encode("ascii"))
    epc_hex_data += RfidConvert.to_hex_from_ushort(a16_bit_field)

    epc = RfidWrite(mem_block=RfidMemBlockEnum.EPC, data=epc_hex_data)
    lbl.add_object(epc)

    user_hex_data = RfidConvert.to_hex_from_ascii_string("MyUserData")
    user_hex_data += "0ABCDE0F"
    user_mem = RfidWrite(mem_block=RfidMemBlockEnum.USER, data=user_hex_data)
    user_mem.offset_from_start = 2
    lbl.add_object(user_mem)

    return lbl


def bcd_maxicodes():
    Defaults.set_printer_resolution(
        PrintResolution(dots_per_unit=203, unit=ScaleEnum.INCH)
    )

    lbl = Label(name="MaxiBcds")

    maxi_data_struct_carrier = MaxicodeMsgStructured(
        mode=MaxicodeModeEnum.MODE2,
        postal_code="902557317",
        country_code="800",
        service_class="200",
        remaining_msg="Maxicode Carrier Standard",
    )
    maxicode_barcode_sc = MaxicodeBarcode(
        start=Points(x=0.5, y=0.5), data=maxi_data_struct_carrier
    )
    maxicode_barcode_sc.ruler = Ruler(scale=ScaleEnum.INCH)

    maxi_data = MaxicodeMsg(
        mode=MaxicodeModeEnum.MODE4,
        primary_msg="123456789",
        remaining_msg="Maxicode unstructured",
    )
    maxicode_barcode = MaxicodeBarcode(start=Points(x=0.5, y=3.5), data=maxi_data)
    maxicode_barcode.ruler = Ruler(scale=ScaleEnum.INCH)

    lbl.add_object(maxicode_barcode_sc)
    lbl.add_object(maxicode_barcode)

    return lbl


def bcd_data_matrix():
    lbl = Label(name="DMatrixBcds")

    Defaults.set_printer_resolution(
        PrintResolution(dots_per_unit=600, unit=ScaleEnum.INCH)
    )
    Defaults.set_ruler(Ruler(scale=ScaleEnum.INCH))

    dflt_matrix = DataMatrixBarcode(
        start=Points(x=0.25, y=0.25), data="Default DataMatrix"
    )
    rect_matrix = DataMatrixBarcode(
        start=Points(x=1.25, y=0.25), data="Rectangular DataMatrix"
    )
    rect_matrix.rotation = RotateEnum.COUNTER_CLOCKWISE
    rect_matrix.rectangle = True
    rect_matrix.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))

    dflt_matrix_multi_line = DataMatrixBarcode(
        start=Points(x=2.25, y=0.25), data="Line 1 DataMatrix"
    )
    eol = dflt_matrix_multi_line.ctrl_char(0x0D) + dflt_matrix_multi_line.ctrl_char(
        0x0A
    )
    dflt_matrix_multi_line.data += eol + "Line 2 content" + eol + "Line 3 content"

    rect_matrix_user_defined_dimensions = DataMatrixBarcode(
        start=Points(x=1.25, y=1.75), data="DataMatrix with user defined dimensions"
    )
    rect_matrix_user_defined_dimensions.rectangle = True
    rect_matrix_user_defined_dimensions.rows_cols = (16, 36)
    rect_matrix_user_defined_dimensions.cell_size = CellSquare(
        xdim=0.030, ruler=Ruler(scale=ScaleEnum.INCH)
    )

    lbl.add_object(dflt_matrix)
    lbl.add_object(rect_matrix)
    lbl.add_object(dflt_matrix_multi_line)
    lbl.add_object(rect_matrix_user_defined_dimensions)

    return lbl


def bcd_aztec():
    lbl = Label(name="AztecBcodes")

    Defaults.set_printer_resolution(
        PrintResolution(dots_per_unit=300, unit=ScaleEnum.INCH)
    )
    Defaults.set_ruler(Ruler(scale=ScaleEnum.INCH))

    some_text = "Mr. AirTraveler, seat A, flight 200"

    bcd_default = AztecBarcode(start=Points(x=0.25, y=1.0), data=some_text)
    bcd_default.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))

    bcd_fixed_err_corr = AztecBarcode(start=Points(x=1.5, y=1.0), data=some_text)
    bcd_fixed_err_corr.cell_size = CellSquare(
        xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
    )
    bcd_fixed_err_corr.type = AztecCodeTypeEnum.FIXED_ERR_CORRECTION
    bcd_fixed_err_corr.fixed_err_correction = 30

    bcd_compact = AztecBarcode(start=Points(x=0.25, y=2.25), data=some_text)
    bcd_compact.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))
    bcd_compact.type = AztecCodeTypeEnum.COMPACT
    bcd_compact.layers = 4

    bcd_full = AztecBarcode(start=Points(x=1.5, y=2.25), data=some_text)
    bcd_full.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))
    bcd_full.type = AztecCodeTypeEnum.FULL
    bcd_full.layers = 5

    bcd_rune_a = AztecBarcode(start=Points(x=0.25, y=4.00), data="0")
    bcd_rune_a.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))
    bcd_rune_a.type = AztecCodeTypeEnum.RUNE

    bcd_rune_b = AztecBarcode(start=Points(x=0.75, y=4.00), data="255")
    bcd_rune_b.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))
    bcd_rune_b.type = AztecCodeTypeEnum.RUNE

    bcd_rune_c = AztecBarcode(start=Points(x=1.25, y=4.00), data="123")
    bcd_rune_c.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))
    bcd_rune_c.type = AztecCodeTypeEnum.RUNE

    lbl.add_object(bcd_default)
    lbl.add_object(bcd_fixed_err_corr)
    lbl.add_object(bcd_full)
    lbl.add_object(bcd_compact)
    lbl.add_object(bcd_rune_a)
    lbl.add_object(bcd_rune_b)
    lbl.add_object(bcd_rune_c)

    return lbl


def bcd_qr_code():
    lbl = Label(name="QRCodes")

    Defaults.set_printer_resolution(
        PrintResolution(dots_per_unit=300, unit=ScaleEnum.INCH)
    )
    Defaults.set_ruler(Ruler(scale=ScaleEnum.INCH))

    en_text = "Tree in the forest"
    ja_text = "森の中の木"

    english = QRBarcode(start=Points(x=0.25, y=1.0), data=en_text)
    english.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))

    english_masked = QRBarcode(start=Points(x=1.5, y=1.0), data=en_text)
    english_masked.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))
    english_masked.mask = QRCodeMaskEnum.MASK4

    japanese = QRBarcode(start=Points(x=0.25, y=2.25), data=ja_text)
    japanese.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))
    japanese.mask = QRCodeMaskEnum.MASK1

    japanese_masked = QRBarcode(start=Points(x=1.5, y=2.25), data=ja_text)
    japanese_masked.cell_size = CellSquare(
        xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
    )
    japanese_masked.mask = QRCodeMaskEnum.MASK4

    auto_enc_data = QRBarcode(
        start=Points(x=0.25, y=3.75), data="12345678 TREE IN THE FOREST 森の中の木"
    )
    auto_enc_data.cell_size = CellSquare(xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH))
    auto_enc_data.mask = QRCodeMaskEnum.MASK4

    manual_mode_data = [
        [QRCodeManualEncodingEnum.NUMERIC, "12345678"],
        [QRCodeManualEncodingEnum.ALPHA_NUMERIC, " TREE IN THE FOREST "],
        [QRCodeManualEncodingEnum.BINARY, "森の中の木"],
    ]

    manual_enc_data = QRBarcode(
        start=Points(x=1.75, y=3.75), manually_encoded_data=manual_mode_data
    )
    manual_enc_data.cell_size = CellSquare(
        xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
    )
    manual_enc_data.mask = QRCodeMaskEnum.MASK4

    lbl.add_object(english)
    lbl.add_object(english_masked)
    lbl.add_object(japanese)
    lbl.add_object(japanese_masked)
    lbl.add_object(auto_enc_data)
    lbl.add_object(manual_enc_data)

    return lbl


# 測試代碼
picture_label = tspl_picture()
print(f"Picture Label: \n{picture_label}")

label = bcd_pdf417()
print(f"Label: \n{label}")

simple_label = simple_text_label(name="Mr. Milky Cheese", address="123 No Way Road")
print(f"SimpleTextLabel: \n{simple_label}")

rfid_label = rfid_encode()
print(f"RfidLabel: \n{rfid_label}")

maxicodes_label = bcd_maxicodes()
print(f"MaxicodesLabel: \n{maxicodes_label}")

data_matrix_label = bcd_data_matrix()
print(f"DataMatrixLabel: \n{data_matrix_label}")

aztec_label = bcd_aztec()
print(f"AztecLabel: \n{aztec_label}")

qr_code_label = bcd_qr_code()
print(f"QRCodeLabel: \n{qr_code_label}")
