import json
import aiosmtplib.errors
import initialization as ini

from flask import Flask, app, render_template, redirect, abort
import os
from dotenv import load_dotenv

from data import db_session
from data.database_structure import *
from data.forms import *

from handlers.get_data_from_files import *
from handlers.form_files import *
from handlers.async_handlers import start_sending_process

app = Flask(__name__, template_folder=os.path.abspath('./static/templates'))
app.config['SECRET_KEY'] = 'LI7-accounting__'


@app.route("/", methods=["GET", "POST"])
def main_page():
    form = Upload1Form()
    context = {
        'form': form,
        'title': 'Upload file',
    }

    if form.validate_on_submit():
        _, extension = os.path.splitext(form.file1.data.filename)
        if extension not in ('.xls', '.xlsx', '.xlsm'):
            context['error_msg'] = "Неподдерживаемый тип файла"
            return render_template('main_page.html', **context)

        file_data = form.file1.data.read()

        db_sess = db_session.create_session()
        file = File(
            file_name=form.file1.data.filename,
            file=file_data
        )

        db_sess.add(file)
        db_sess.commit()

        with open(DOWNLOADED_FILES_PATH + rf'\{file.modified_date.strftime("%d-%m-%Y")}.xlsm', 'wb') as f:
            f.write(file_data)

        settings = db_sess.query(Settings).first()

        try:
            emails_data = settings.decode_jwt()
        except AttributeError:
            context['error_msg'] = "Файл с настройками не загружен"
            return render_template('main_page.html', **context)
        except jwt.exceptions.DecodeError:
            context['error_msg'] = "Файл с адресами эл.почт не загружен"
            return render_template('main_page.html', **context)

        try:
            start_sending_process(file_data, emails_data, settings.qr_pattern)
        # except aiosmtplib.errors.SMTPAuthenticationError:
        #     context['error_msg'] = "Некорректный email"
        #     from handlers.async_handlers import loop
        #     loop.close()
        #     return render_template('main_page.html', **context)
        except KeyError:
            context['error_msg'] = "Excel файл не соответствует шаблону"
            return render_template('main_page.html', **context)

        return redirect('/')
    return render_template('main_page.html', **context)


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    sender_form = SettingsForm()
    receipt_form = Upload1Form()
    emails_form = Upload2Form()
    context = {
        'sender_form': sender_form,
        'receipt_form': receipt_form,
        'emails_form': emails_form,
        'title': 'Settings',
    }

    db_sess = db_session.create_session()
    settings = db_sess.query(Settings).first()
    if settings:
        context["placeholder"] = settings.sender_email
    else:
        context["placeholder"] = ""

    if receipt_form.validate_on_submit():
        _, extension = os.path.splitext(receipt_form.file1.data.filename)
        if extension not in ('.xls', '.xlsx', '.xlsm'):
            context['error_msg'] = "Неподдерживаемый тип файла"
            return render_template('settings_page.html', **context)

        file_bytes_data = receipt_form.file1.data.read()
        try:
            file_data_in_dict = parse_settings(file_bytes_data)
        except KeyError:
            context['error_msg'] = "Excel файл не соответствует шаблону"
            return render_template('settings_page.html', **context)

        db_sess = db_session.create_session()
        _settings = db_sess.query(Settings).filter(Settings.id == 1).first()
        if not _settings:
            _settings = Settings(
                receipt_file=fill_receipt_sender_params(file_data_in_dict)
            )
        else:
            _settings.receipt_file = fill_receipt_sender_params(file_data_in_dict)

        _settings.set_qr_pattern(file_data_in_dict)

        db_sess.add(_settings)
        db_sess.commit()

    if emails_form.validate_on_submit():
        _, extension = os.path.splitext(emails_form.file2.data.filename)
        if extension not in ('.xls', '.xlsx', '.xlsm'):
            context['error_msg'] = "Неподдерживаемый тип файла"
            return render_template('settings_page.html', **context)

        file_bytes_data = emails_form.file2.data.read()
        try:
            file_data_in_dict = parse_emails(file_bytes_data)
        except KeyError:
            context['error_msg'] = "Excel файл не соответствует шаблону"
            return render_template('settings_page.html', **context)

        db_sess = db_session.create_session()
        _settings = db_sess.query(Settings).filter(Settings.id == 1).first()
        if not _settings:
            _settings = Settings()

        _settings.encode_jwt(file_data_in_dict)

        db_sess.add(_settings)
        db_sess.commit()

    if sender_form.validate_on_submit():
        db_sess = db_session.create_session()
        _settings = db_sess.query(Settings).filter(Settings.id == 1).first()
        if not _settings:
            _settings = Settings(
                sender_email=sender_form.email.data
            )
        else:
            _settings.sender_email = sender_form.email.data

        _pswrd = ini.var_data["PASSWORD"]
        _var_data = ini.var_data

        _var_data["FROM"] = sender_form.email.data
        ini.write_file(_var_data)

        db_sess.add(_settings)
        db_sess.commit()

    return render_template('settings_page.html', **context)


@app.route("/history", methods=["GET"])
def history_page():
    context = {
        'title': 'History',
        'files': []
    }

    for path in os.listdir('./static/downloaded_files'):
        context['files'].append((f"/static/downloaded_files/{path}", path))

    return render_template('history_page.html', **context)


@app.route("/documentation")
def docs_page():
    return render_template('docs_page.html')


def main():
    load_dotenv()
    db_directory = os.path.join(os.getcwd(), r'database')
    if not os.path.exists(db_directory):
        os.mkdir(db_directory)
    db_session.global_init("database/accounting.db")

    port = ini.var_data["PORT"]
    host = ini.var_data["HOST"]
    app.debug = False
    app.run(host=host, port=port)
