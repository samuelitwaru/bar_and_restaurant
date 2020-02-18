from flask import Flask
from flask_login import LoginManager
from Application import configuration
from Application.database.model import User, session
from flask_mail import Mail

app = Flask(__name__)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).filter_by(id=user_id).first()


app.config.from_object(configuration.DevelopmentConfig)

mail = Mail(app)


from Application.blueprints.Category.category import category
from Application.blueprints.Brand.brand import brand
from Application.blueprints.KitchenStock.kitchen_stock import kitchen_stock
from Application.blueprints.Purchase.purchase import purchase
from Application.blueprints.PurchaseGuide.purchase_guide import purchase_guide
from Application.blueprints.SaleGuide.sale_guide import sale_guide
from Application.blueprints.Sale.sale import sale
from Application.blueprints.Order.order import order
from Application.blueprints.KitchenStockPurchase.kitchen_stock_purchase import kitchen_stock_purchase
from Application.blueprints.KitchenStockUsage.kitchen_stock_usage import kitchen_stock_usage

from Application.blueprints.FoodCategory.food_category import food_category
from Application.blueprints.Food.food import food

from Application.blueprints.Cashier.cashier import cashier
from Application.blueprints.Waiter.waiter import waiter
from Application.blueprints.Chef.chef import chef
from Application.blueprints.Manager.manager import manager

from Application.blueprints.User.user import user
from Application.blueprints.Session.sess import sess

from Application.blueprints.Email.email import email

app.register_blueprint(category)
app.register_blueprint(brand)
app.register_blueprint(kitchen_stock)
app.register_blueprint(purchase)
app.register_blueprint(purchase_guide)
app.register_blueprint(sale_guide)
app.register_blueprint(sale)
app.register_blueprint(order)
app.register_blueprint(kitchen_stock_purchase)
app.register_blueprint(kitchen_stock_usage)

app.register_blueprint(food_category)
app.register_blueprint(food)

app.register_blueprint(cashier)
app.register_blueprint(waiter)
app.register_blueprint(chef)
app.register_blueprint(manager)

app.register_blueprint(user)
app.register_blueprint(sess)

app.register_blueprint(email)