import os

import openpyxl

from handlers.secondary_functions import make_file
from CONSTANTS import *


def parse_settings(data):
    make_file(data, FILES_PATH + r"\settings.xlsx")

    settings_book = openpyxl.load_workbook(FILES_PATH + r"\settings.xlsx")
    settings_sheet = settings_book['Настройки']
    names_values = [v[0].value for v in settings_sheet['A2':'A12']]
    params_values = [v[0].value for v in settings_sheet['B2':'B12']]

    os.remove(FILES_PATH + r"\settings.xlsx")

    params = {key: value for key, value in list(zip(names_values, params_values))}

    # params['pattern'] = data["Шаблон"]
    # params['org_name'] = data['Наименование организации']
    # params['inn'] = data['ИНН']
    # params['kpp'] = data['КПП']
    # params['bik'] = data['БИК']
    # params['corr_account'] = data['Корреспондентский счет']
    # params['bank_name'] = data['Наименование банка']
    # params['payment_account'] = data['Расчетный счет']
    # params['service_code'] = data['Код услуги']
    # params['dsk'] = data['Дополнительные параметры ДШК']

    return params


def parse_payers(data):
    """
    This function parses payers' data from table(Name, number, etc.)
    :return: parsed list
    """
    make_file(data, FILES_PATH + r"\payers.xlsx")

    receipt_book = openpyxl.load_workbook(FILES_PATH + r"\payers.xlsx")

    sheet = receipt_book['Реестр начислений']

    parsed = [tuple(map(lambda x: x.value, row)) for row in sheet.iter_rows(min_row=7)]

    # os.remove("payers.xlsx")

    return parsed


def parse_emails(data):
    """
    This function parses payers' emails from table.
    :return: parsed list
    """
    make_file(data, FILES_PATH + r"\emails.xlsx")

    receipt_book = openpyxl.load_workbook(FILES_PATH + r"\emails.xlsx")

    sheet = receipt_book['emails']

    parsed = {row[0].value: row[1].value
              for row in sheet.iter_rows(min_row=2)}

    # os.remove("emails.xlsx")

    return parsed
