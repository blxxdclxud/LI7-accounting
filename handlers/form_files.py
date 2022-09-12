import os

import convertapi
import openpyxl
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from handlers.secondary_functions import *
from handlers.mail_sender import send_email
from CONSTANTS import *


def fill_receipt_sender_params(data):
    receipt_book = openpyxl.load_workbook(FILES_PATH + r"\blank_receipt_pattern.xlsx")

    sheet = receipt_book['receipt']
    col = sheet['C']

    col[1].value = data['Наименование организации']
    col[3].value = f"  ИНН {data['ИНН']} КПП {data['КПП']}{25 * ' '}{data['Расчетный счет']}"
    col[5].value = f"БИК {data['БИК']} ({data['Наименование банка']})"
    col[14].value = col[1].value
    col[16].value = col[3].value
    col[18].value = col[5].value

    receipt_book.save(FILES_PATH + r"\receipt_pattern.xlsx")

    # with open("blank_receipt_pattern.xlsx", 'rb') as receipt_file:
    #     content = receipt_file.read()

    convertapi.api_secret = 'yyKssjcTKewwZvnx'
    res = convertapi.convert('pdf', {"File": FILES_PATH + r'\receipt_pattern.xlsx'}, from_format='xlsx')
    res.file.save(FILES_PATH)

    with open(FILES_PATH + r'\receipt_pattern.xlsx', 'rb') as receipt_file:
        content = receipt_file.read()

    return content


async def fill_and_send_personal_receipts(payers_data, qr_pattern, server, email, num=None):
    """
    This function fills receipts for each payer and sends it to payer's email.

    :param payers_data: formatted payers data parsed from table
    :param qr_pattern: the values pattern for QR-code
    :return: None
    """

    for payer in payers_data:
        # создаем объект-холст, для добавления текста в PDF файл
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        # добавляем свой шрифт
        pdfmetrics.registerFont(TTFont('Arial', FONTS_PATH + r'\Arial Cyr Regular.ttf'))
        can.setFont('Arial', 9)

        # добавляем два текста, разделенных на отдельные строки (табельный номер, ФИО и т.п.)
        _start_height = 723
        for _ in range(2):
            count = 0
            for section in center(
                    f"Табельный номер ребенка: {payer[0].strip()}; Код группы: {payer[1].strip()}               "
                    f"; ФИО ребенка: {payer[2].strip()}                      ;Период: {get_date(payer[3]).strip()}",
                    87).split('\n'):
                can.drawString(166, _start_height + count, text=section)
                count -= 12
            _start_height = 538

        # задаем размер шрифта для другого текста
        can.setFont('Arial', 8)
        # добавляем первый текст (Сумма оплаты)
        can.drawCentredString(353, 687, f"Сумма: {get_amount(payer[4])}")
        # добавляем второй текст (Сумма оплаты)
        can.drawCentredString(353, 504, f"Сумма: {get_amount(payer[4])}")

        # создаем QR-код по данным плательщика и добавляем его на холст
        make_qr(make_qr_data(qr_pattern, payers_data[0]))
        can.drawInlineImage(FILES_PATH + r"\qr_code.png", 40, 485, 120, 120, anchor='u')
        # переносим объект текст на холст
        can.save()

        # открываем PDF файл
        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        can.showPage()
        existing_pdf = PdfFileReader(open(FILES_PATH + r"\receipt_pattern.pdf", "rb"))
        # добавляем наш холст в PDF файл
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        # записываем в новый файл
        output = PdfFileWriter()
        output.addPage(page)
        output_stream = open(FILES_PATH + rf"\dest_{num}.pdf", "wb")
        output.write(output_stream)
        output_stream.close()

        await send_email(email, "Квитанция", "Оплата", FILES_PATH + rf"\dest_{num}.pdf", server)
        os.remove(FILES_PATH + rf"\dest_{num}.pdf")
        # break

