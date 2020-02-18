from flask import Blueprint, render_template, url_for, request, redirect, jsonify, flash
from Application.database.model import Brand, Food, Category, FoodCategory, Order, Sale, Waiter, Cashier, Session, SaleGuide, session
from flask_login import login_required, current_user
from Application.blueprints import utils
import json
import datetime

sale = Blueprint('sale', __name__, url_prefix="/sale")

module = sale.name


@sale.route("")
@login_required
def sales():
    categories = Category.read(Category)
    food_categories = FoodCategory.read(FoodCategory)
    waiters = Waiter.read(Waiter)
    return render_template("cashier/sales.html", mod=module, categories=categories, food_categories=food_categories, waiters=waiters)


@sale.route("/get-sale-items", methods=["GET"])
@login_required
def get_sale_items():
    foods = Food.read(Food)
    drinks = Brand.read(Brand)
    sale_items = utils.build_sale_items_dict(foods, drinks)
    return jsonify(sale_items)


@sale.route("/", methods=["POST"])
@login_required
def add_sales():
    if request.method == "POST":
        sales = request.form["sales"]
        waiter_id = request.form["waiter"]
        cashier_id = request.form["cashier"]
        customer = request.form["customer"]

        waiter = Waiter.read_one(Waiter, waiter_id)
        cashier = Cashier.read_one(Cashier, cashier_id)

        new_order = Order(customer, waiter, cashier)

        sales = json.loads(sales)
        food_sales = sales["food_items"]
        drink_sales = sales["drink_items"]

        verified_bill = 0

        for drink_sale in drink_sales.values():
            brand = Brand.read_one(Brand, drink_sale["id"])
            reduce_quantity = float(drink_sale["quantity"]) / float(drink_sale["quantity_ratio"])
            Sale(drink_sale["sale_unit"], drink_sale["sale_price"], drink_sale["quantity"], new_order, waiter, cashier, brand=brand, reduce_quantity=reduce_quantity, sale_guide_id=drink_sale["sale_guide_id"])
            verified_bill += int(drink_sale["quantity"]) * int(drink_sale["sale_price"])

        for food_sale in food_sales.values():
            food = Food.read_one(Food, food_sale["id"])
            reduce_quantity = float(food_sale["quantity"]) / float(food_sale["quantity_ratio"])
            Sale(food_sale["sale_unit"], food_sale["sale_price"], food_sale["quantity"], new_order, waiter, cashier, food=food, reduce_quantity=reduce_quantity)
            verified_bill += int(food_sale["quantity"]) * int(food_sale["sale_price"])

        new_order.bill = verified_bill
        current_session = Session.get_current_session(Session, current_user.cashier)
        current_session.orders.append(new_order)
        session.commit()
        flash("Order submitted successfully", "success")
        order_id = new_order.id
        session.close()
        return redirect(url_for('order.get_order', id=order_id))


@sale.route("/sales", methods=["GET"])
@login_required
def get_sales():
    sales = Sale.read(Sale)
    sale_page = Sale.read_limit(Sale, 1, 10)
    cashiers = Cashier.read(Cashier)
    waiters = Waiter.read(Waiter)
    items = Food.read(Food) + Brand.read(Brand)
    total_sales = utils.compute_sales(sales)
    return render_template("manager/sales.html", mod=module, sales=sales, sale_page=sale_page, total_sales=total_sales, cashiers=cashiers, waiters=waiters, items=items)


@sale.route("/sale_page", methods=["GET"])
@login_required
def get_sale_page():
    page = request.args.get("page")
    if page:
        page = int(page)
        if page == 0:
            return redirect(url_for('sale.get_sales'))
        sale_page = Sale.read_limit(Sale, page, 10)
        sales = sale_page.items
        cashiers = Cashier.read(Cashier)
        waiters = Waiter.read(Waiter)
        items = Food.read(Food) + Brand.read(Brand)
        total_sales = utils.compute_sales(sales)
        return render_template("manager/sales.html", mod=module, sales=sales, sale_page=sale_page, current_page=page, total_sales=total_sales, cashiers=cashiers,
                           waiters=waiters, items=items)
    else:
        return redirect(url_for("sale.get_sales"))


@sale.route("/food_sales", methods=["GET"])
@login_required
def get_food_sales():
    if request.args.get("page"):
        page = int(request.args.get("page"))
        if page == 0:
            return redirect(url_for('sale.get_food_sales'))
    else:
        page = 1
    sale_page = Sale.read_food_sales(Sale, page, 10)
    sales = sale_page.items
    cashiers = Cashier.read(Cashier)
    waiters = Waiter.read(Waiter)
    items = Food.read(Food)
    total_sales = utils.compute_sales(sales)
    return render_template("chef/food-sales.html", mod=module, sales=sales, sale_page=sale_page, current_page=page, total_sales=total_sales, cashiers=cashiers, waiters=waiters, items=items)


@sale.route("/filter", methods=["GET"])
@login_required
def filter_sales():
    if request.method == "GET":
        cashiers = Cashier.read(Cashier)
        waiters = Waiter.read(Waiter)
        items = Food.read(Food) + Brand.read(Brand)
        
        item = request.args["item"]
        cashier = request.args["cashier"]
        waiter = request.args["waiter"]
        _from = request.args["from"]
        to = request.args["to"]

        if _from:
            _from = utils.convert_date_from_html(_from)
        else:
            _from = datetime.datetime(2000, 1, 1)
        if to:
            to = utils.convert_date_from_html(to)
        else:
            to = datetime.datetime(9999, 12, 31)

        sales = Sale.filter(Sale, item, cashier, waiter, _from, to)
        total_sales = utils.compute_sales(sales)

        # Avoid error on changing str to int
        if cashier == "":
            cashier = 0
        if waiter == "":
            waiter = 0

        return render_template("manager/sales.html", mod=module, sales=sales, total_sales=total_sales, cashiers=cashiers, waiters=waiters, items=items, today=_from, tomorrow=to, item_id=item, cashier_id=int(cashier), waiter_id=int(waiter))


@sale.route("/filter_food", methods=["GET"])
@login_required
def filter_food():
    if request.method == "GET":
        cashiers = Cashier.read(Cashier)
        waiters = Waiter.read(Waiter)
        items = Food.read(Food)

        item = request.args["item"]
        cashier = request.args["cashier"]
        waiter = request.args["waiter"]
        _from = request.args["from"]
        to = request.args["to"]

        if _from:
            _from = utils.convert_date_from_html(_from)
        else:
            _from = datetime.datetime(2000, 1, 1)
        if to:
            to = utils.convert_date_from_html(to)
        else:
            to = datetime.datetime(3000, 1, 1)

        if item == '0':
            return redirect(url_for('sale.get_food_sales'))

        sales = Sale.filter(Sale, item, cashier, waiter, _from, to)
        total_sales = utils.compute_sales(sales)

        # Avoid error on changing str to int
        if cashier == "":
            cashier = 0
        if waiter == "":
            waiter = 0

        return render_template("chef/food-sales.html", mod=module, sales=sales, total_sales=total_sales,
                                   cashiers=cashiers, waiters=waiters, items=items, today=_from, tomorrow=to,
                                   item_id=item, cashier_id=int(cashier), waiter_id=int(waiter))