from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    RadioField, FileField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Length


class SettingsForm(FlaskForm):
    email = EmailField("Введите адрес эл.почты, с которой будут отправляться письма",
                       validators=[DataRequired()])
    submit = SubmitField("Сохранить")


class Upload1Form(FlaskForm):
    file1 = FileField("", validators=[DataRequired()])
    submit = SubmitField("Обработать")


class Upload2Form(FlaskForm):
    file2 = FileField("", validators=[DataRequired()])
    submit = SubmitField("Обработать")
