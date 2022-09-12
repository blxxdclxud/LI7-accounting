from math import ceil
import qrcode
from datetime import datetime
from CONSTANTS import FILES_PATH


def center(string, length):
    """
    This function formats a string to convenient format (separates it on strings)
    :param string: string to be formatted
    :param length: maximum length of separated string-line
    """
    reserve = ''
    for i in range(ceil(len(string) / length)):
        string = string.strip()
        if string.find(' ', length) != -1:
            cur = string[:string.find(' ', length)]
        else:
            cur = string
        if string[:length + 1][-1] == ' ':
            string = string[length + 1:]
        else:
            if len(cur) > length:
                idx = cur.rfind(' ')
                cur = cur[:idx]
                string = string[idx:]

        reserve += cur.center(83) + '\n'

    return reserve


def make_qr(qr_data):
    """This function makes a QR-code from given data"""

    qr = qrcode.QRCode(border=1, box_size=4)
    qr.add_data(qr_data)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(FILES_PATH + r"\qr_code.png")


def make_qr_data(qr_pattern, data):
    data_list = qr_pattern.split('~')
    for idx in range(len(data_list[:-1])):
        if idx == 4:
            if '.' not in str(data[idx]) or ',' not in str(data[idx]):
                data_list[idx] += str(data[idx]).strip() + "00"
            else:
                data_list[idx] += str(data[idx]).strip().replace('.', '').replace(',', '')
        elif idx == 3:
            data_list[idx] += get_date(str(data[idx]).strip(), mode='receipt')
        else:
            data_list[idx] += str(data[idx]).strip().upper()

    return ''.join(data_list)


def get_date(date, mode='filename'):
    """
    This function formats date to convenient format
    :param date: date to be formatted
    :return: formatted date
    """
    months = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь',
    }

    if mode == 'receipt':
        formatted_date = datetime.strptime(date, "%d.%m.%Y")
        formatted_date = formatted_date.strftime("%m") + str(formatted_date.year)[2:]
    else:
        formatted_date = datetime.strptime(date, "%d.%m.%Y")
        formatted_date = months[formatted_date.month] + " " + str(formatted_date.year)

    return formatted_date


def get_amount(amount):
    """
    This function formats account value to convenient format
    :param amount: amount
    :return: formatted amount string
    """
    formatted_amount = str(amount).replace(',', '.').split('.')
    if len(formatted_amount) == 1:
        formatted_amount.append('00')
    return f"{formatted_amount[0]} руб. {formatted_amount[1]} коп."


def make_file(data, filename):
    """
    This function creates file with given filename and writes data to it.
    :param data: bytes-format file's data
    :param filename: name of the new file
    :return:
    """
    with open(filename, 'wb') as receipt_file:
        receipt_file.write(data)
