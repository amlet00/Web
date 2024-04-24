from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired


class BalanceForm(FlaskForm):
    money = IntegerField("Карта уже есть введите сумму", validators=[DataRequired()])

    submit = SubmitField("Подтвердить")
