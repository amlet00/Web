from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired


class OrderForm(FlaskForm):
    amount_pizza1 = IntegerField('Количество пиццы Пеперони', default=0)
    amount_pizza2 = IntegerField('Количество пиццы Маргарита', default=0)
    amount_pizza3 = IntegerField('Количество пиццы Гавайской', default=0)

    submit = SubmitField('Заказать')


class CanceledOrderForm(FlaskForm):
    reason = StringField('Причина', validators=[DataRequired()])

    submit = SubmitField('Подтвердить')
