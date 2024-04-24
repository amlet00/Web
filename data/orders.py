import datetime
import sqlalchemy

from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase, create_session
from .pizza import Pizza


class Orders(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    customer_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"))
    order = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    total_price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    reason = sqlalchemy.Column(sqlalchemy.String, default='')
    start_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                   default=datetime.datetime.now)

    user = orm.relationship('User')

    def __repr__(self):
        return f"<Order> {self.order}"

    def order_to_dict(self):
        my_dict = {}
        for line in self.order.split(','):
            db_sess = create_session()
            pizza_id, amount = map(int, line.split(':'))
            pizza = db_sess.query(Pizza).get(pizza_id)
            my_dict[pizza] = amount
        return my_dict
