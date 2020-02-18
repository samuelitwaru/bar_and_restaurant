from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, DateTime, Boolean, and_, desc
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy_pagination import paginate
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import max

import os
from datetime import datetime
from random import randint, choice

basedir = os.path.abspath(os.path.dirname(__file__))
path = 'sqlite:////' + os.path.join(basedir, 'data.sqlite')
engine = create_engine(path)
session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


class FoodCategory(Base):
    __tablename__ = "food_category"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    foods = relationship("Food", backref="category")

    def __init__(self, name):
        self.name = name
        session.add(self)
        session.commit()

    def read(self):
        return session.query(self).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, name):
        self.name = name
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


class Food(Base):
    __tablename__ = "food"
    id = Column(Integer, primary_key=True)
    food_ref = Column(String)
    name = Column(String(64), unique=True)
    units_available = Column(Integer)
    sale_unit = Column(String)
    sale_price = Column(Integer)
    category_id = Column(Integer, ForeignKey("food_category.id"))
    sales = relationship("Sale", backref="food")

    def __init__(self, name, units_available, sale_unit, sale_price, category):
        self.name = name.replace("/", "-")
        self.units_available = units_available
        self.sale_unit = sale_unit
        self.sale_price = sale_price
        session.add(self)
        category.foods.append(self)
        self.food_ref = self.create_ref()
        session.commit()

    def read(self):
        return session.query(self).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).first()

    def update(self, name, sale_unit, sale_price, category):
        self.name = name.replace("/", "-")
        self.sale_unit = sale_unit
        self.sale_price = sale_price
        category.foods.append(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def update_units(self, units):
        self.units_available += int(units)
        session.commit()

    def reduce_quantity(self, quantity):
        self.units_available -= quantity

    def create_ref(self):
        return (("f-"+str(self.id)+"-"+str(randint(1000, 9999))).replace(" ", "").replace("/", "-")).lower()


class KitchenStock(Base):
    __tablename__ = "kitchen_stock"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    quantity_available = Column(Float(2), default=0.0)
    usage_unit = Column(String)
    kitchen_stock_purchases = relationship("KitchenStockPurchase", backref="kitchen_stock")
    kitchen_stock_usages = relationship("KitchenStockUsage", backref="kitchen_stock")

    def __init__(self, name, usage_unit):
        self.name = name.replace("/", "-")
        self.usage_unit = usage_unit
        session.add(self)
        session.commit()

    def read(self):
        return session.query(self).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, name, usage_unit):
        self.name = name.replace("/", "-")
        self.usage_unit = usage_unit
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def add_quantity(self, quantity):
        self.quantity_available += float(quantity)
        session.commit()

    def reduce_quantity(self, quantity):
        self.quantity_available -= round(quantity, 2)
        session.commit()


class KitchenStockPurchase(Base):
    __tablename__ = "kitchen_stock_purchase"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now())
    purchase_unit = Column(String)
    unit_price = Column(Integer)
    purchase_quantity = Column(Integer)
    added_stock_quantity = Column(Integer)
    added_stock_unit = Column(String)
    chef_name = Column(String)
    kitchen_stock_name = Column(String)
    kitchen_stock_id = Column(Integer, ForeignKey("kitchen_stock.id"))
    chef_id = Column(Integer, ForeignKey("chef.id"))

    def __init__(self, purchase_unit, unit_price, purchase_quantity, added_stock_quantity, added_stock_unit, user, stock):
        self.purchase_unit = purchase_unit
        self.unit_price = unit_price
        self.purchase_quantity = purchase_quantity
        self.added_stock_quantity = added_stock_quantity
        self.added_stock_unit = added_stock_unit
        self.kitchen_stock_name = stock.name
        if user.chef:
            self.chef_name = " ".join([user.chef.first_name, user.chef.last_name])
            user.chef.kitchen_stock_purchases.append(self)
        elif user.manager:
            self.chef_name = " ".join([user.manager.first_name, user.manager.last_name, "(Manager)"])
        stock.kitchen_stock_purchases.append(self)
        stock.add_quantity(added_stock_quantity)
        session.add(self)
        session.commit()

    def read(self):
        return session.query(self).order_by(desc("date")).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).first()

    def delete(self):
        session.delete(self)
        session.commit()

    def read_limit(self, number, limit):
        page = paginate(session.query(self).order_by(desc("date")), number, limit)
        return page

    def filter(self, item, chef, _from, to):
        return session.query(self).filter(self.kitchen_stock_id.like("%"+item), self.chef_id.like("%"+chef), and_(self.date >= _from, self.date <= to)).order_by(desc("date")).all()

    def filter2(self, item, _from, to, filter_kitchen):
        if filter_kitchen:
            return session.query(self).filter(self.kitchen_stock_id.like("%"+item), and_(self.date >= _from, self.date <= to)).order_by(desc("date")).all()
        return []

    def get_total_price(self, **kwargs):
        purchases = kwargs.get("purchases")
        if purchases == None:
            purchases = self.read(self)
        return sum([(purchase.purchase_quantity * purchase.unit_price) for purchase in purchases])


class KitchenStockUsage(Base):
    __tablename__ = "kitchen_stock_usage"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now())
    stock_name = Column(String)
    quantity = Column(Integer)
    unit = Column(String)
    chef_name = Column(String)
    chef_id = Column(Integer, ForeignKey("chef.id"))
    kitchen_stock_id = Column(Integer, ForeignKey("kitchen_stock.id"))

    def __init__(self, stock, quantity, chef):
        self.stock_name = stock.name
        self.quantity = quantity
        self.unit = stock.usage_unit
        self.chef_name = " ".join([chef.first_name, chef.last_name])
        session.add(self)
        chef.kitchen_stock_usages.append(self)
        session.commit()

    def read(self):
        return session.query(self).order_by(desc("date")).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).first()

    def delete(self):
        session.delete(self)
        session.commit()

    def read_limit(self, number, limit):
        page = paginate(session.query(self).order_by(desc("date")), number, limit)
        return page

    def filter(self, item, chef, _from, to):
        return session.query(self).filter(self.kitchen_stock_id.like("%"+item), self.chef_id.like("%"+chef), and_(self.date >= _from, self.date <= to)).order_by(desc("date")).all()


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    brands = relationship("Brand", backref="category")

    def __init__(self, name):
        self.name = name.replace("/","-")
        session.add(self)
        session.commit()

    def read(self):
        return session.query(self).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, name):
        self.name = name.replace("/","-")
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def add_brand(self, brand):
        self.brands.append(brand)


class Brand(Base):
    __tablename__ = "brand"
    id = Column(Integer, primary_key=True)
    brand_ref = Column(String, unique=True)
    name = Column(String(64), unique=True)
    quantity_available = Column(Float(2))
    category_id = Column(Integer, ForeignKey("category.id"))
    purchase_guide_id = Column(Integer, ForeignKey("purchase_guide.id"))
    sale_guides = relationship("SaleGuide", backref="brand")
    purchases = relationship("Purchase", backref="brand")
    sales = relationship("Sale", backref="brand")

    def __init__(self, name, quantity_available, category, purchase_guide):
        self.name = name.replace("/","-")
        self.quantity_available = quantity_available
        session.add(self)
        purchase_guide.set_brand(self)
        category.add_brand(self)
        self.brand_ref = self.create_ref()
        session.commit()

    def read(self):
        return session.query(self).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, name, category):
        self.name = name.replace("/","-")
        category.add_brand(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def add_sale_guide(self, sale_guide):
        self.sale_guides.append(sale_guide)

    def add_quantity(self, quantity):
        self.quantity_available += float(quantity)
        session.commit()

    def reduce_quantity(self, quantity):
        self.quantity_available -= round(quantity, 2)

    def update_quantity(self, quantity):
        self.quantity_available += float(quantity)

    def add_purchase(self, purchase):
        self.purchases.append(purchase)
        session.commit()

    def create_ref(self):
        return (("b-"+str(self.id)+"-"+str(randint(1000, 9999))).replace(" ", "").replace("/", "-")).lower()


class PurchaseGuide(Base):
    __tablename__ = "purchase_guide"
    id = Column(Integer, primary_key=True)
    purchase_unit = Column(String(64))
    purchase_price = Column(Integer)
    brand = relationship(Brand, backref="purchase_guide", uselist=False)

    def __init__(self, purchase_unit, purchase_price):
        self.purchase_unit = purchase_unit
        self.purchase_price = purchase_price
        session.add(self)
        session.commit()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, purchase_unit, purchase_price):
        self.purchase_unit = purchase_unit
        self.purchase_price = purchase_price
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def set_brand(self, brand):
        self.brand = brand


class SaleGuide(Base):
    __tablename__ = "sale_guide"
    id = Column(Integer, primary_key=True)
    sale_unit = Column(String(64))
    sale_price = Column(Integer)
    quantity_in_purchase_unit = Column(Integer)
    brand_id = Column(Integer, ForeignKey("brand.id"))

    def __init__(self, sale_unit, sale_price, quantity_in_purchase_unit, brand):
        self.sale_unit = sale_unit
        self.sale_price = sale_price
        self.quantity_in_purchase_unit = quantity_in_purchase_unit
        session.add(self)
        brand.add_sale_guide(self)
        session.commit()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).first()

    def delete(self):
        session.delete(self)
        session.commit()


class Purchase(Base):
    __tablename__ = "purchase"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now())
    purchase_unit = Column(String)
    purchase_price = Column(Integer)
    quantity = Column(Integer)
    brand_id = Column(Integer, ForeignKey("brand.id"))

    def __init__(self, purchase_unit, purchase_price, quantity, brand):
        self.purchase_unit = purchase_unit
        self.purchase_price = purchase_price
        self.quantity = quantity
        brand.add_purchase(self)
        session.add(self)
        session.commit()

    def read(self):
        return session.query(self).order_by(desc("date")).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).first()

    def delete(self):
        session.delete(self)
        session.commit()

    def read_limit(self, number, limit):
        page = paginate(session.query(self).order_by(desc("date")), number, limit)
        return page

    def filter(self, id, _from, to, filter_bar):
        if filter_bar:
            return session.query(self).filter(self.brand_id.like("%"+id), and_(self.date >= _from, self.date <= to)).order_by(desc("date")).all()
        return []

    def get_total_price(self, **kwargs):
        purchases = kwargs.get("purchases")
        if purchases == None:
            purchases = self.read(self)
        return sum([(purchase.quantity * purchase.purchase_price) for purchase in purchases])


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    order_ref = Column(String, unique=True)
    date = Column(DateTime, default=datetime.now())
    bill = Column(Integer)
    paid = Column(Integer, default=0)
    customer = Column(String)
    open = Column(Boolean, default=True)
    waiter_id = Column(Integer, ForeignKey("waiter.id"))
    cashier_id = Column(Integer, ForeignKey("cashier.id"))
    sales = relationship("Sale", backref="order")
    session_id = Column(Integer, ForeignKey("session.id"))

    def __init__(self, customer, waiter, cashier):
        self.order_ref = self.create_ref()
        self.customer = customer
        cashier.orders.append(self)
        waiter.orders.append(self)

    def read(self):
        return session.query(self).order_by(desc("date")).all()

    def read_limit(self, number, limit):
        page = paginate(session.query(self).order_by(desc("date")), number, limit)
        return page

    def read_one(self, id):
        return session.query(self).filter_by(id=id).first()

    def create_ref(self):
        return "OASIS-O-"+str(randint(1000, 9999))+"-"+datetime.now().strftime("%d%m%Y")

    def update_payment(self, payment):
        self.paid += payment
        session.commit()

    def update_info(self, cashier, waiter, customer, paid):
        self.cashier = cashier
        self.waiter = waiter
        self.customer = customer
        self.paid = paid
        session.commit()

    def close(self):
        self.open = False
        session.commit()

    def _open(self):
        self.open = True
        session.commit()

    def filter(self, open, cashier, waiter, _from, to):
        return session.query(self).filter(self.cashier_id.like("%"+cashier), self.open.like("%"+open), self.waiter_id.like("%"+waiter), and_(self.date >= _from, self.date <= to)).order_by(desc("date")).all()

    def search_customer(self, search_string, session_id):
        if session_id:
            return session.query(self).filter(self.customer.like("%"+search_string+"%"), self.session_id.like(session_id)).order_by(desc("date")).all()
        else:
            return session.query(self).filter(self.customer.like("%" + search_string + "%")).order_by(desc("date")).all()

    def read_cashier_orders(self, cashier_id):
        return session.query(self).filter_by(cashier_id=cashier_id).order_by(desc("date")).all()

    def calculate_bill(self):
        return sum([(sale.sale_price*sale.quantity) for sale in self.sales])


class Sale(Base):
    __tablename__ = "sale"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now())
    sale_unit = Column(String)
    sale_price = Column(Integer)
    quantity = Column(Integer)
    brand_id = Column(Integer, ForeignKey("brand.id"))
    sale_guide_id = Column(Integer, ForeignKey("sale_guide.id"))
    food_id = Column(Integer, ForeignKey("food.id"))
    order_id = Column(Integer, ForeignKey("order.id"))
    cashier_id = Column(Integer, ForeignKey("cashier.id"))
    waiter_id = Column(Integer, ForeignKey("waiter.id"))

    def __init__(self, sale_unit, sale_price, quantity, order, waiter, cashier, **kwargs):
        self.sale_unit = sale_unit
        self.sale_price = sale_price
        self.quantity = quantity
        self.sale_guide_id = kwargs.get("sale_guide_id")
        order.sales.append(self)
        waiter.sales.append(self)
        cashier.sales.append(self)
        brand = kwargs.get("brand")
        food = kwargs.get("food")
        reduce_quantity = kwargs.get("reduce_quantity")
        if brand:
            brand.sales.append(self)
            brand.reduce_quantity(reduce_quantity)
        elif food:
            food.sales.append(self)
            food.reduce_quantity(reduce_quantity)

    def read(self):
        return session.query(self).order_by(desc("date")).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).first()

    def read_food_sales(self, number, limit):
        page = paginate(session.query(self).filter(self.food_id != None).order_by(desc("date")), number, limit)
        return page

    def filter(self, item, cashier, waiter, _from, to):
        if item == "all":
            return session.query(self).filter(self.cashier_id.like("%"+cashier), self.waiter_id.like("%"+waiter), and_(self.date >= _from, self.date <= to)).order_by(desc("date")).all()
        else:
            item_type, item_id = item.split("-")
            if item_type == "drink":
                return session.query(self).filter(self.brand_id == item_id, self.cashier_id.like("%"+cashier), self.waiter_id.like("%"+waiter), and_(self.date >= _from, self.date <= to)).order_by(desc("date")).all()
            elif item_type == "food":
                return session.query(self).filter(self.food_id == item_id, self.cashier_id.like("%"+cashier), self.waiter_id.like("%"+waiter), and_(self.date >= _from, self.date <= to)).order_by(desc("date")).all()

    def read_limit(self, number, limit):
        page = paginate(session.query(self).order_by(desc("date")), number, limit)
        return page


class Waiter(Base):
    __tablename__ = "waiter"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    orders = relationship("Order", backref="waiter")
    sales = relationship("Sale", backref="waiter")

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        session.add(self)
        session.commit()

    def read(self):
        return session.query(self).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


class Cashier(Base):
    __tablename__ = "cashier"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    sales = relationship("Sale", backref="cashier")
    orders = relationship("Order", backref="cashier")
    sessions = relationship("Session", backref="cashier")
    user = relationship("User", backref="cashier", cascade="all,delete", uselist=False)

    def __init__(self, first_name, last_name, user):
        self.first_name = first_name
        self.last_name = last_name
        session.add(self)
        user.set_cashier(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def read(self):
        return session.query(self).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, first_name, last_name, username):
        self.first_name = first_name
        self.last_name = last_name
        self.user.username = username
        session.commit()

    def update_password(self, password):
        self.user.password = generate_password_hash(password)
        session.commit()

    def get_current_session(self):
        return Session.get_current_session(Session, self)


class Session(Base):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    stop_time = Column(DateTime)
    cash = Column(Integer)
    cashier_id = Column(Integer, ForeignKey("cashier.id"))
    orders = relationship("Order", backref="session")

    def __init__(self, cashier):
        self.start_time = datetime.now()
        cashier.sessions.append(self)
        session.add(self)
        session.commit()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).first()

    def read(self):
        return session.query(self).order_by(desc("start_time")).all()

    def read_limit(self, number, limit):
        page = paginate(session.query(self).order_by(desc("start_time")), number, limit)
        return page

    def get_current_session(self, cashier):
        return session.query(self).filter_by(cashier_id=cashier.id, cash=None, stop_time=None).first()

    def update(self, cash):
        self.cash = cash
        self.stop_time = datetime.now()
        session.commit()

    def filter(self, cashier, _from, to):
        return session.query(self).filter(self.cashier_id.like("%"+cashier), and_(self.start_time >= _from, self.start_time <= to)).order_by(desc("start_time")).all()

    def get_total_sales(self):
        total_sales = 0
        for order in self.orders:
            total_sales += sum([(sale.quantity * sale.sale_price) for sale in order.sales])
        return total_sales


class Chef(Base):
    __tablename__ = "chef"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    admin = Column(Boolean)
    user = relationship("User", backref="chef", cascade="all,delete", uselist=False)
    kitchen_stock_usages = relationship("KitchenStockUsage", backref="chef")
    kitchen_stock_purchases = relationship("KitchenStockPurchase", backref="chef")

    def __init__(self, first_name, last_name, admin, user):
        self.first_name = first_name
        self.last_name = last_name
        self.admin = admin
        session.add(self)
        user.set_chef(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def read(self):
        return session.query(self).all()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, first_name, last_name, admin, username):
        self.first_name = first_name
        self.last_name = last_name
        self.admin = admin
        self.user.username = username
        session.commit()

    def update_password(self, password):
        self.user.password = generate_password_hash(password)
        session.commit()


class Manager(Base):
    __tablename__ = "manager"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    email = Column(String(64))
    boss_email = Column(String(64))
    user = relationship("User", backref="manager", cascade="all,delete", uselist=False)

    def __init__(self, first_name, last_name, email, boss_email, user):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.boss_email = boss_email
        session.add(self)
        user.set_manager(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    def read(self):
        return session.query(self).all()

    def get_by_email(self, email):
        return session.query(self).filter_by(email=email).first()

    def read_one(self, id):
        return session.query(self).filter_by(id=id).one()

    def update(self, first_name, last_name, email, username, boss_email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.user.username = username
        self.boss_email = boss_email
        session.commit()

    def update_password(self, password):
        self.user.password = generate_password_hash(password)
        session.commit()


class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(64))
    password = Column(String)
    cashier_id = Column(Integer, ForeignKey("cashier.id", ondelete="CASCADE"))
    manager_id = Column(Integer, ForeignKey("manager.id", ondelete="CASCADE"))
    chef_id = Column(Integer, ForeignKey("chef.id", ondelete="CASCADE"))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)
        session.add(self)

    def delete(self):
        session.delete(self)
        session.commit()

    def set_cashier(self, cashier):
        self.cashier = cashier

    def set_manager(self, manager):
        self.manager = manager

    def set_chef(self, chef):
        self.chef = chef

    def find_user(self, username, password):
        users = session.query(self).filter_by(username=username).all()
        if len(users) == 1:
            user = users[0]
            if check_password_hash(user.password, password):
                return user
            else:
                return False
        else:
            return False

    def get_role(self):
        if self.cashier_id:
            return "cashier"
        elif self.manager_id:
            return "manager"
        elif self.chef_id:
            return "chef"

class Email(Base):
    __tablename__ = 'email'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.now())

    def __init__(self):
        session.add(self)
        session.commit()

    def get_latest(self):
        return session.query(self, max(self.time).label('time')).first()


if __name__ == "__main__":
    print('restarting model...')
    try:
        os.remove("data.sqlite")
    except FileNotFoundError:
        print('db not found')
    Base.metadata.create_all(bind=engine)

    food_categories = {
        "Pastas": ["Spaghetti Nappolitana", "Spaoghetti Carbonara"],
        "Pizza Corner": ["Margareta", "Oasis 24-7 Deluxe Pizza","Hawii PIzza","Regina Pizza", "Vegetarian Pizza", "Chicken Pizza", ],
        "Beverage": ["African Tea or Coffee", "Black Tea or Coffee", "Hot Chocalate", "English Tea or Coffee", "Glass of Hot Milk"],
        "Juices": ["Pineapple Juice", "Water Melon", "Cocktail Juice", "Frute Platter"],
        "Burgers": ["Beef Burger", "Chicken Burger", "Vegetable Burger", "Cheese Burger", "Egg Burger"],
        "Sandwiches": ["Chicken Sandwich", "Beef sandwich", "Egg sandwich", "Cheeses sandwich"],
        "Chicken Tatys": ["Grilled Chicken Chips", "Garlic Chicken Chips", "Chicken Stew"],
        "Beef or Goat": ["Beef Stir-fry"],
        "Oasis Mixed Grill": ["OX Liver"],
        "Goat": ["Pan Fried Goat", "Goat Stew"],
        "Fish": ["Fish Tillet", "Fish Fingers"],
        "Snacks": ["Beef Samosa", "Vegetable Samosa", "Chicken Wings", "Chips Plain", "Chips Masala", "Chicken Drum Stick", "Egg Plain", "Chapati", "Mandazi", "G.nuts"],
        "Salad": ["Garden Salad", "Chef Salad"],
        "Soups": ["Cream of Tomato Soup", "Cream of Mushroom", "Chicken Clear Soup", "Beans Sauce", "Pork Plain", "Chicken Plain", "Goat Plain"]
    }

    brand_categories = {
        "Beer or AFBs": ["Nile Special 500ml", "Nile Special 330ml", "Club Pilsner 500ml", "Club Pilsner 330ml", "Club Twist 330ml", "Eagle Dark 300ml", "Castle Lager 440ml", "Castle Lite 330ml", "Castle Milk Stout 330ml", "Redds Preminum", "Ice Double Black", "Bell Lager", "Guiness 500ml", "Smirnoff Red", "Smirnoff Black"],
        "Energy Drink" : ["Red Bull", "String", "Alvaro", "Coke", "Pepsi", "Coke Plastic 500ml"],
        "Wines and Wisky": ["Red Wines Sweet", "Red Wine", "White Wine Sweet", "White Wine Dry", "Zappa Red", "Zappa Green" "Tequilla", "Amanla", "MC Dowels", "Captain Morgan", "South Comfort", "Four Cousins", "Baileys"],
        "Red Label": ["Red Label", "Red Label 200ml", "Red Label 350ml", "Red Label 750ml", "Red Label 1 Litre"],
        "Black Label": ["Black Label", "Black Label 200ml", "Black Label 350ml", "Black Label 750ml", "Black Label 1 Litre"],
    }


    Manager
    user = User("samit", "123")
    manager = Manager("Samuel", "Itwaru", "samuelitwaru@yahoo.com", "samuelitwaru@yahoo.com", user)

    # Cashier
    user2 = User("josh", "123")
    cashier = Cashier("Byenkya", "Joshua", user2)

    # Chef
    user3 = User("mutesi", "123")
    chef = Chef("Mutesi", "Wilbrod", True, user3)

    # Waiter
    waiter = Waiter("Okot", "Smith")

    # Kitchen Stock
    kitchen_stock = [("Ginger", "Kilograms"), ("Oil", "Litres"), ("Tomatoes", "Pieces"), ("Onions", "Pieces"), ("Cabbage", "Heads")]
    for name, usage_unit in kitchen_stock:
        KitchenStock(name, usage_unit)

    # Food Categories
    for food_category, foods in food_categories.items():
        cat = FoodCategory(food_category)
        for food in foods:
            Food(food, choice(range(15, 100)), "Plate", choice(range(1000, 40000, 500)), cat)

    #Drink Categories
    for drink_category, brands in brand_categories.items():
        cat = Category(drink_category)
        for brand in brands:
            price = choice(range(1000, 20000, 500))
            pg = PurchaseGuide("Bottle", price)
            brand = Brand(brand, choice(range(15, 100)), cat, pg)
            sg = SaleGuide("Bottle", price + 1000, 10, brand)

    Email()

    import time
    time.sleep(10)

    Email()



    session.close()