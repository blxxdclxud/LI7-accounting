import sys
import asyncio
import time
import os
import aiosmtplib

import initialization as ini

from handlers.form_files import fill_and_send_personal_receipts
from handlers.get_data_from_files import parse_payers, parse_emails


async def load_data(data, emails, qr_pattern):
    tasks = []

    _var_data = ini.var_data

    _from = _var_data["FROM"]
    host = _var_data["EMAIL_HOST"]
    port = _var_data["EMAIL_PORT"]
    password = _var_data["PASSWORD"]
    # st = time.time()
    # print(host, port)
    server = aiosmtplib.SMTP(hostname=host, port=port, use_tls=True)
    await server.connect()
    await server.login(_from, password)
    # et = time.time()
    # print(et - st)
    print(data[0][0])
    #    print(emails)
    for idx in range(len(data)):
        print("!!!!!!", data[idx], emails, data[idx][1].strip(), emails[data[idx][1].strip()])
        try:
            _personal_email = emails[data[idx][1].strip()]
        except KeyError:
            raise KeyError(f"Ошибка с эл.почтой у {data[idx][1].strip()}")

        task = asyncio.create_task(fill_and_send_personal_receipts(
            [data[idx]],
            qr_pattern,
            server,
            _personal_email,
            num=idx))
        tasks.append(task)

    await asyncio.gather(*tasks)
    await server.quit()


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
loop = asyncio.get_event_loop()


def start_sending_process(payers_table_data, emails_data, qr_pattern):
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # loop = asyncio.get_event_loop()

    payers_data = parse_payers(payers_table_data)
    # start_time = time.time()
    asyncio.run(load_data(payers_data, emails_data, qr_pattern))
    # end_time = time.time()
    # print(end_time - start_time)
