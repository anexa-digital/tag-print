import os
from UniPRT.LabelMaker.PGL.RfidWrite import RfidWrite
from UniPRT.LabelMaker.PGL.Label import Label
from UniPRT.LabelMaker.PGL.Shapes import Line, Box
from UniPRT.LabelMaker.PGL.BcdMaxicode import (
    MaxicodeMsgStructured,
    MaxicodeBarcode,
    MaxicodeMsg,
    MaxicodeModeEnum,
    MaxicodeMsgStructuredOpenSystemStandard,
)
from UniPRT.LabelMaker.PGL.BcdDataMatrix import DataMatrixBarcode
from UniPRT.LabelMaker.PGL.BcdAztec import AztecBarcode
from UniPRT.LabelMaker.PGL.Pdf417Barcode import Pdf417Barcode
from UniPRT.LabelMaker.PGL.Barcode1D import Barcode1D, BarcodeTypeEnum1D, BarWidths
from UniPRT.LabelMaker.PGL.QRBarcode import QRBarcode
from UniPRT.LabelMaker.PGL.Text import Text
from UniPRT.LabelMaker.Interfaces.IRfid import RfidMemBlockEnum
from UniPRT.LabelMaker.Interfaces.IBcdQRCode import QRCodeMaskEnum, QRCodeManualEncodingEnum
from UniPRT.LabelMaker.Interfaces.ISettings import RotateEnum, AlignEnum
from UniPRT.LabelMaker.Interfaces.IBcdPdf417 import Pdf417ErrCorrectionEnum
from UniPRT.LabelMaker.Interfaces.IBarcode2D import CellRect, CellSquare
from UniPRT.LabelMaker.Interfaces.IBarcode1D import BarcodeItem
from UniPRT.LabelMaker.Interfaces.Defaults import Defaults
from UniPRT.LabelMaker.Interfaces.ICoordinates import MM_PER_INCH
from UniPRT.LabelMaker.Interfaces.IBcdAztec import AztecCodeTypeEnum
from UniPRT.LabelMaker.Interfaces.Coordinate import (
    Ruler,
    ScaleEnum,
    PrintResolution,
    Points,
)
from UniPRT.LabelMaker.Interfaces.RfidConvert import RfidConvert
from UniPRT.LabelMaker.Interfaces.IFont import (
    FontSizeUnitsEnum,
    FontSize,
    FontStyleEnum,
)
from UniPRT.LabelMaker.Interfaces.IText import TextItem

from UniPRT.LabelMaker.PGL.PglPicture import PglPicture
from UniPRT.LabelMaker.PglLib.PglUtilities import PglWindowsFontWithImageName

from pathlib import Path

class PglPictures:
    def __call__(self):
        lbl = Label(name="PglPictureTest")

        Defaults.set_printer_resolution(PrintResolution(dots_per_unit=200, unit=ScaleEnum.INCH))
        Defaults.set_ruler(Ruler(scale=ScaleEnum.INCH))

        picture = PglPicture(start=Points(x=0.25, y=0.25), image_name="qwe")
        lbl.add_object(picture)

        font_data = PglWindowsFontWithImageName(
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
            print(f"Font data written to: {file_path}")
        except Exception as e:
            print(f"Failed to write font data: {e}")

        return lbl
    
def file_replace(path_and_name: str, data_to_write: str):
    try:
        with open(path_and_name, "w", encoding="utf-8") as file:
            file.write(data_to_write)
    except Exception as e:
        print(f"Error writing file: {str(e)}")


def string_to_hex(input_str: str) -> str:
    return "".join(format(ord(char), "02X") for char in input_str)


class PglRfidEncode:
    def __call__(self):
        lbl = Label(name="RfidLbl")

        a32_bit_field = 0x11223344
        a16_bit_field = 0xBEEF
        a6_char_ascii_string = "MyData"

        epc_hex_data = f"{a32_bit_field:08X}{string_to_hex(a6_char_ascii_string)}{a16_bit_field:04X}"
        epc = RfidWrite(mem_block=RfidMemBlockEnum.EPC, data=epc_hex_data)
        lbl.add_object(epc)

        user_data_hex = f"{string_to_hex('MyUserData')}0ABCDE0F"
        user_mem = RfidWrite(mem_block=RfidMemBlockEnum.USER, data=user_data_hex)
        user_mem.offset_from_start = 2
        lbl.add_object(user_mem)

        return lbl


class PglBcdPdf417:
    def __call__(self):
        lbl = Label(name="Pdf417Bcodes")
        Defaults.set_printer_resolution(
            PrintResolution(dots_per_unit=600, unit=ScaleEnum.INCH)
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

        bcd_rows_limited = Pdf417Barcode(
            start=Points(x=0.25, y=3.00), data=some_short_text
        )
        bcd_rows_limited.cell_size = CellRect(
            xdim=0.015, ydim=0.050, ruler=Ruler(scale=ScaleEnum.INCH)
        )
        bcd_rows_limited.rows = 15

        bcd_cols_limited = Pdf417Barcode(
            start=Points(x=0.25, y=4.00), data=some_short_text
        )
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


class PglBcdAztec:
    def __call__(self):
        lbl = Label(name="AztecBcodes")
        Defaults.set_printer_resolution(
            PrintResolution(dots_per_unit=300, unit=ScaleEnum.INCH)
        )
        Defaults.set_ruler(Ruler(scale=ScaleEnum.INCH))

        some_text = "Mr. AirTraveler, seat A, flight 200"

        bcd_default = AztecBarcode(start=Points(x=0.25, y=1.0), data=some_text)
        bcd_default.cell_size = CellSquare(
            xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
        )

        bcd_fixed_err_corr = AztecBarcode(start=Points(x=1.5, y=1.0), data=some_text)
        bcd_fixed_err_corr.cell_size = CellSquare(
            xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
        )
        bcd_fixed_err_corr.type = AztecCodeTypeEnum.FIXED_ERR_CORRECTION
        bcd_fixed_err_corr.fixed_err_correction = 30

        bcd_compact = AztecBarcode(start=Points(x=0.25, y=2.25), data=some_text)
        bcd_compact.cell_size = CellSquare(
            xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
        )
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
        lbl.add_object(bcd_compact)
        # lbl.add_object(bcd_full)
        # lbl.add_object(bcd_rune_a)
        lbl.add_object(bcd_rune_b)
        # lbl.add_object(bcd_rune_c)

        return lbl


class PglBcdQRCode:
    def __call__(self):
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
        english_masked.cell_size = CellSquare(
            xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
        )
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
        auto_enc_data.cell_size = CellSquare(
            xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
        )
        auto_enc_data.mask = QRCodeMaskEnum.MASK4

        manual_mode_data = [
            [QRCodeManualEncodingEnum.NUMERIC, "12345678"],
            [QRCodeManualEncodingEnum.ALPHA_NUMERIC, " TREE IN THE FOREST "],
            [QRCodeManualEncodingEnum.BINARY, "森の中の木"],
        ]

        manual_enc_data = QRBarcode(
            start=Points(x=1.75, y=3.75), data_manually_encoded=manual_mode_data
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


class PglBcdDataMatrix:
    def __call__(self):
        lbl = Label(name="DMatrixBcds")
        Defaults.set_printer_resolution(
            PrintResolution(dots_per_unit=300, unit=ScaleEnum.INCH)
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
        rect_matrix.cell_size = CellSquare(
            xdim=0.025, ruler=Ruler(scale=ScaleEnum.INCH)
        )

        dflt_matrix_multi_line = DataMatrixBarcode(
            start=Points(x=2.25, y=0.25), data="Line 1 DataMatrix"
        )
        eol = dflt_matrix_multi_line.ctrl_char(0x0D) + dflt_matrix_multi_line.ctrl_char(
            0x0A
        )
        dflt_matrix_multi_line.data = (
            f"{dflt_matrix_multi_line.data}{eol}Line 2 content{eol}Line 3 content"
        )

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


class PglBcdMaxicodes:
    def __call__(self):
        lbl = Label(name="MaxiBcds")

        maxi_data_struct_carrier = MaxicodeMsgStructured(
            mode=MaxicodeModeEnum.MODE2,
            postal_code="90255",
            country_code="800",
            service_class="200",
            remaining_msg="Maxicode Carrier Standard",
        )
        maxicode_barcode_sc = MaxicodeBarcode(
            start=Points(x=0.5, y=0.5), data=maxi_data_struct_carrier
        )
        maxicode_barcode_sc.ruler = Ruler(scale=ScaleEnum.INCH)

        maxi_data_oss = MaxicodeMsgStructuredOpenSystemStandard(
            mode=MaxicodeModeEnum.MODE3,
            year="24",
            postal_code="OHA123",
            country_code="123",
            service_class="400",
            remaining_msg="Maxicode Open Standard Format",
        )
        maxicode_barcode_oss = MaxicodeBarcode(
            start=Points(x=0.5, y=2.0), data=maxi_data_oss
        )
        maxicode_barcode_oss.ruler = Ruler(scale=ScaleEnum.INCH)

        maxi_data = MaxicodeMsg(
            mode=MaxicodeModeEnum.MODE4,
            primary_msg="123456789",
            remaining_msg="Maxicode unstructured",
        )
        maxicode_barcode = MaxicodeBarcode(start=Points(x=0.5, y=3.5), data=maxi_data)
        maxicode_barcode.ruler = Ruler(scale=ScaleEnum.INCH)

        lbl.add_object(maxicode_barcode_sc)
        lbl.add_object(maxicode_barcode_oss)
        lbl.add_object(maxicode_barcode)

        return lbl


class PglSimpleLabel:
    def __call__(self, name: str, address: str):
        lbl = Label(name="SimpleLabel")

        inch_ruler = Ruler(scale=ScaleEnum.INCH)
        mm_ruler = Ruler(scale=ScaleEnum.MM)

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

        box1 = Box(
            start=Points(x=0.5, y=1.25),
            end=Points(x=3.5, y=2.25),
            line_thickness=1.0 / 16.0,
        )
        box1.ruler = inch_ruler
        lbl.add_object(box1)

        product_text = Text()
        product_text.font_size_units = FontSizeUnitsEnum.RULER
        product_text.ruler = inch_ruler
        product_text.alignment = AlignEnum.CENTER
        product_text.font_name = "93952.sf"

        text_item1 = TextItem(start=Points(x=2.0, y=1.25 + 7.0 / 16.0), data="MY MAGIC")
        text_item1.font_size = FontSize(x=3.0 / 16.0, y=7.0 / 16.0)
        product_text.text.append(text_item1)

        text_item2 = TextItem(
            start=Points(x=2.0, y=1.25 + 1.0 - 3.0 / 16.0), data="PRODUCT"
        )
        text_item2.font_size = FontSize(x=3.0 / 16.0, y=7.0 / 16.0)
        product_text.text.append(text_item2)

        lbl.add_object(product_text)

        bold_to_from = Text()
        bold_to_from.font_size_units = FontSizeUnitsEnum.RULER
        bold_to_from.ruler = mm_ruler
        bold_to_from.font_style = FontStyleEnum.BOLD
        bold_to_from.font_name = "92248.sf"

        bold_text_item1 = TextItem(start=Points(x=5.0, y=5.0), data="TO:")
        bold_text_item1.font_size = FontSize(x=2.5, y=5.0)
        bold_to_from.text.append(bold_text_item1)

        bold_text_item2 = TextItem(
            start=Points(x=(2.5 + 1 / 16.0) * 25.4, y=5.0), data="FROM:"
        )
        bold_to_from.text.append(bold_text_item2)

        lbl.add_object(bold_to_from)

        company_name = Text()
        company_name.font_size_units = FontSizeUnitsEnum.PERCENT
        company_name.ruler = mm_ruler
        company_name.font_style = FontStyleEnum.ITALIC
        company_name.font_name = "92500.sf"

        company_name_text_item = TextItem(
            start=Points(x=(2.5 + 1 / 16.0 + 1 / 8.0) * 25.4, y=17.0), data="Happy Inc."
        )
        company_name_text_item.font_size = FontSize(x=2.0, y=3.0)
        company_name.text.append(company_name_text_item)

        lbl.add_object(company_name)

        name_txt = Text()
        name_txt.font_size_units = FontSizeUnitsEnum.RULER
        name_txt.ruler = mm_ruler
        name_txt.font_style = FontStyleEnum.ITALIC

        name_text_item = TextItem(start=Points(x=8.0, y=10.0), data=name)
        name_text_item.font_size = FontSize(x=2.5, y=5.0)
        name_txt.text.append(name_text_item)

        lbl.add_object(name_txt)

        address_txt = Text()
        address_txt.ruler = mm_ruler

        address_text_item = TextItem(start=Points(x=8.0, y=17.0), data=address)
        address_txt.text.append(address_text_item)

        lbl.add_object(address_txt)

        bcd128 = Barcode1D(
            barcode=BarcodeItem(
                start=Points(x=0.5, y=(1.5 + 1 / 4.0 + 1.2)),
                height=1.2,
                data="Code 128",
            )
        )
        bcd128.barcode_type = BarcodeTypeEnum1D.CODE128
        bcd128.print_human_readable = True
        bcd128.rotation = RotateEnum.NONE
        bcd128.ruler = inch_ruler
        bcd128.bar_widths = BarWidths(narrow_bar=0.015, wide_bar=0.015 * 4.1)
        bcd128.bar_widths.ruler = inch_ruler
        lbl.add_object(bcd128)

        bcd93 = Barcode1D(
            barcode=BarcodeItem(
                start=Points(x=0.5, y=3.5 - 1 / 8.0 - 0.6), height=0.6, data="CODE 93"
            )
        )
        bcd93.barcode_type = BarcodeTypeEnum1D.CODE93
        bcd93.print_human_readable = True
        bcd93.rotation = RotateEnum.NONE
        bcd93.ruler = inch_ruler
        bcd93.bar_widths = BarWidths(narrow_bar=0.025, wide_bar=0.025 * 4.1)
        bcd93.bar_widths.ruler = inch_ruler
        lbl.add_object(bcd93)

        dm_customer = DataMatrixBarcode(start=Points(x=2.7, y=4.0), data=name)
        dm_customer.cell_size = CellSquare(xdim=0.040, ruler=inch_ruler)
        dm_customer.ruler = inch_ruler
        eol = dm_customer.ctrl_char(0x0D) + dm_customer.ctrl_char(0x0A)
        dm_customer.data = f"{dm_customer.data}{eol}{address}"
        lbl.add_object(dm_customer)

        return lbl


class RulerLines:
    def __call__(
        self, length: float, vertical: bool, inch_units: bool, margin: float
    ) -> list:
        ruler_lines = []
        tick_ruler = Ruler(scale=ScaleEnum.INCH if inch_units else ScaleEnum.MM)

        ruler_length = length
        tick_thickness = 0.010
        tick_length = 1 / 16.0
        ticks_per_unit = 16.0 if inch_units else 1.0

        if not inch_units:
            tick_thickness *= MM_PER_INCH
            tick_length *= MM_PER_INCH
            margin *= MM_PER_INCH

        ruler_length -= tick_thickness

        for i in range(1, int(ruler_length * ticks_per_unit) + 1):
            tick = tick_length
            if inch_units:
                if i % 16 == 0:
                    tick *= 3.5
                elif i % 8 == 0:
                    tick *= 2.5
                elif i % 4 == 0:
                    tick *= 2.0
                elif i % 2 == 0:
                    tick *= 1.5
            else:
                if i % 10 == 0:
                    tick *= 3.0
                elif i % 5 == 0:
                    tick *= 1.5

            tick_line = Line.from_coordinates(
                x_start=margin if vertical else i / ticks_per_unit,
                y_start=i / ticks_per_unit if vertical else margin,
                x_end=margin + tick if vertical else i / ticks_per_unit,
                y_end=i / ticks_per_unit if vertical else margin + tick,
                line_thickness=tick_thickness,
            )
            tick_line.ruler = tick_ruler
            ruler_lines.append(tick_line)

        return ruler_lines


class RuleredLabel:
    def __call__(
        self, width: float, length: float, inch_units: bool, ruler_margin: float
    ) -> Label:
        ver_ruler_ticks = RulerLines()(
            length=length, vertical=True, inch_units=inch_units, margin=ruler_margin
        )
        hor_ruler_ticks = RulerLines()(
            length=width, vertical=False, inch_units=inch_units, margin=ruler_margin
        )

        Defaults.set_printer_resolution(
            PrintResolution(dots_per_unit=300, unit=ScaleEnum.INCH)
        )

        ruler_lbl = Label(name="Ruler")
        for tick_line in ver_ruler_ticks:
            ruler_lbl.add_object(tick_line)
        for tick_line in hor_ruler_ticks:
            ruler_lbl.add_object(tick_line)

        return ruler_lbl


if __name__ == "__main__":

    pgl_picture = PglPictures()()
    print(f"PGLPicture: \n{pgl_picture}")

    pgl_label = PglRfidEncode()()
    print(f"RfidEncode: \n{pgl_label}")

    pgl_pdf417_label = PglBcdPdf417()()
    print(f"BcdPdf417: \n{pgl_pdf417_label}")

    pgl_aztec_label = PglBcdAztec()()
    print(f"BcdAztec: \n{pgl_aztec_label}")

    pgl_qr_code_label = PglBcdQRCode()()
    print(f"BcdQRCode: \n{pgl_qr_code_label}")

    pgl_data_matrix_label = PglBcdDataMatrix()()
    print(f"BcdDataMatrix: \n{pgl_data_matrix_label}")

    pgl_maxicodes_label = PglBcdMaxicodes()()
    print(f"BcdMaxicodes: \n{pgl_maxicodes_label}")

    pgl_simple_label = PglSimpleLabel()(name="Mr. Einstein", address="123 Relativity Road")
    print(f"SimpleLabel: \n{pgl_simple_label}")

    # rulered_label_inch = RuleredLabel()(width=4.0, length=6.0, inch_units=True, ruler_margin=1.0 / 8.0)
    # print(f"RuleredLabel (Inches): \n{rulered_label_inch}")

    # rulered_label_mm = RuleredLabel()(
    #     width=4.0 * 25.4, length=6.0 * 25.4, inch_units=False, ruler_margin=1.0 / 8.0
    # )
    # print(f"RuleredLabel (MM): \n{rulered_label_mm}")
