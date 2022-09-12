import datetime
import os
import jwt

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class File(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'files'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    file_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now,
                                      nullable=True)


class Settings(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'settings'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    receipt_file = sqlalchemy.Column(sqlalchemy.BINARY, nullable=True)
    emails = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    qr_pattern = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sender_email = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_qr_pattern(self, data):
        pattern = 'ST00012|' \
                  f'Name={data["Наименование организации"]}|' \
                  f'PersonalAcc={data["Расчетный счет"]}|' \
                  f'BankName={data["Наименование банка"]}|' \
                  f'BIC={data["БИК"]}|' \
                  f'CorrespAcc={data["Корреспондентский счет"]}|' \
                  f'PayeeINN={data["ИНН"]}|' \
                  f'KPP={data["КПП"]}|' \
                  f'CHILDKOD=~|' \
                  f'GroupKod=~|' \
                  f'CHILDFIO=~|' \
                  f'paymPeriod=~|' \
                  f'Sum=~|' \
                  f'{data["Дополнительные параметры ДШК"]}'

        self.qr_pattern = pattern

    def encode_jwt(self, data):
        self.emails = jwt.encode(data, 'secret', algorithm="HS256")

    def decode_jwt(self):
        return jwt.decode(self.emails, 'secret', algorithms=["HS256"])
