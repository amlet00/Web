from flask import Flask, render_template
from flask import redirect, abort

from flask_login import LoginManager, login_user, current_user
from flask_login import login_required, logout_user

from flask_restful import Api

from api.users_resourses import UsersListResource, UserResource

from data import db_session

from data.orders import Orders
from data.users import User
from data.pizza import Pizza

from forms.balance import BalanceForm
from forms.order import OrderForm, CanceledOrderForm
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_pizza_secret_key'

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        form.image.data.save(f'static/img/users_images/{form.email.data}.jpg')
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            address=form.address.data,
            image=f'static/img/users_images/{form.email.data}.jpg',
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def menu():
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        return render_template("menu.html", orders=[])
    elif current_user.is_manager:
        orders = db_sess.query(Orders).all()
        list_of_orders_dict = [order.order_to_dict() for order in orders]
    else:
        orders = db_sess.query(Orders).filter(Orders.user == current_user)
        list_of_orders_dict = [order.order_to_dict() for order in orders]
    return render_template("menu.html", title='Меню', orders=orders, list_of_orders_dict=list_of_orders_dict)


@app.route("/balance", methods=['GET', 'POST'])
@login_required
def balance():
    form = BalanceForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        current_user.balance += form.money.data
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect("/")

    return render_template('balance.html', title='Пополнение баланса', form=form)


@app.route("/create_order", methods=['GET', 'POST'])
@login_required
def create_order():
    form = OrderForm()
    db_sess = db_session.create_session()
    pizzas = db_sess.query(Pizza).all()
    pizzas_dict = {}
    for i, pizza in enumerate(pizzas):
        pizzas_dict[f"pizza{i + 1}"] = pizza
    if form.validate_on_submit():
        if any(map(lambda amount: amount > 1000,
                   [form.amount_pizza1.data, form.amount_pizza2.data, form.amount_pizza3.data])):
            return render_template('order.html', title='Создание заказа', form=form, **pizzas_dict,
                                   message="Слишком много пицц")
        if any(map(lambda amount: amount < 0,
                   [form.amount_pizza1.data, form.amount_pizza2.data, form.amount_pizza3.data])):
            return render_template('order.html', title='Создание заказа', form=form, **pizzas_dict,
                                   message="Это как?")
        db_sess = db_session.create_session()
        order = Orders()
        order.order = f'1:{form.amount_pizza1.data},2:{form.amount_pizza2.data},3:{form.amount_pizza3.data}'
        order.total_price = sum([pizzas[i].price * amount for i, amount in enumerate(
                                 [form.amount_pizza1.data, form.amount_pizza2.data, form.amount_pizza3.data])])
        current_user.orders.append(order)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect("/")
    return render_template('order.html', title='Создание заказа', form=form, **pizzas_dict)


@app.route('/delete_order/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_order(id):
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).filter(Orders.id == id, current_user == Orders.user).first()
    if order:
        db_sess.delete(order)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/accept_order/<int:id>', methods=['GET', 'POST'])
@login_required
def accept_order(id):
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).filter(Orders.id == id, current_user.is_manager == 1).first()
    if order:
        order.status = 1
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/cancel_order/<int:id>', methods=['GET', 'POST'])
@login_required
def cancel_order(id):
    form = CanceledOrderForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        order = db_sess.query(Orders).filter(Orders.id == id, current_user.is_manager == 1).first()
        order.reason = form.reason.data
        order.status = 2
        db_sess.commit()
        return redirect("/")

    return render_template('cancel_order.html', title='Пополнение баланса', form=form)


@app.route('/pay_for_order/<int:id>', methods=['GET', 'POST'])
@login_required
def pay_for_order(id):
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).filter(Orders.id == id, current_user == Orders.user).first()
    if order:
        if current_user.balance < order.total_price:
            return render_template('menu.html', title='Меню',
                                   message="Недостаточно средств")
        current_user.balance -= order.total_price
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/pizza.db")
    api.add_resource(UsersListResource, '/api/v2/users')
    api.add_resource(UserResource, '/api/v2/users/<int:user_id>')
    app.run(port=5000, host='127.0.0.1')


if __name__ == '__main__':
    main()
