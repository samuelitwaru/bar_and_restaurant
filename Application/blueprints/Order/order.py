from flask import Blueprint, render_template, url_for, request, redirect, flash, jsonify
from flask_login import current_user, login_required
from Application.database.model import Order, Cashier, Waiter, Session, Food, Brand, Category, FoodCategory, Sale, SaleGuide, session
from Application.blueprints import utils
import datetime
import json

order = Blueprint('order', __name__, url_prefix="/order")

module = order.name


@order.route("/")
@login_required
def get_orders():
    cashiers = Cashier.read(Cashier)
    waiters = Waiter.read(Waiter)
    order_page = Order.read_limit(Order, 1, 10)

    if current_user.manager:
        orders = Order.read(Order)
        total_bill, total_paid = utils.compute_total_bill_and_total_paid_from_orders(orders)
        return render_template("manager/orders.html", order_page=order_page, mod=module, orders=orders, total_bill=total_bill, total_paid=total_paid, waiters=waiters, cashiers=cashiers)
    elif current_user.cashier:
        current_session = Session.get_current_session(Session, current_user.cashier)
        if current_session:
            orders = current_session.orders
            orders.reverse()
            total_bill, total_paid = utils.compute_total_bill_and_total_paid_from_orders(orders)
            return render_template("cashier/orders.html", mod=module, orders=orders, waiters=waiters, total_bill=total_bill, total_paid=total_paid)
        flash("No session was found! Login to start a new session", "info")
        return redirect(url_for('user.logout'))
    elif current_user.chef:
        orders = Order.read(Order)
        return render_template("chef/orders.html", mod=module, orders=orders, waiters=waiters)


@order.route("/order_page", methods=["GET"])
@login_required
def get_order_page():
    page = request.args.get("page")
    if page:
        page = int(page)
        if page == 0:
            return redirect(url_for('order.get_orders'))
        order_page = Order.read_limit(Order, page, 10)
        orders = order_page.items
        cashiers = Cashier.read(Cashier)
        waiters = Waiter.read(Waiter)
        total_bill, total_paid = utils.compute_total_bill_and_total_paid_from_orders(orders)
        print(">>>>>>>>>>>>>>>", total_bill, total_paid)
        return render_template("manager/orders.html", mod=module, orders=orders, total_bill=total_bill, total_paid=total_paid, order_page=order_page, current_page=page, cashiers=cashiers, waiters=waiters)
    else:
        return redirect(url_for("order.get_orders"))


@order.route("/search", methods=["GET"])
@login_required
def search():
    if request.method == "GET":
        search_string = request.args.get("search-string")

        if current_user.cashier:
            current_session = Session.get_current_session(Session, current_user.cashier)

            orders = Order.search_customer(Order, search_string, current_session.id)

            total_bill, total_paid = utils.compute_total_bill_and_total_paid_from_orders(orders)

            cashiers = Cashier.read(Cashier)
            waiters = Waiter.read(Waiter)

            return render_template("cashier/orders.html", mod=module, orders=orders, total_bill=total_bill,
                                       total_paid=total_paid, cashiers=cashiers, waiters=waiters)
        else:
            orders = Order.search_customer(Order, search_string, None)
            total_bill, total_paid = utils.compute_total_bill_and_total_paid_from_orders(orders)

            cashiers = Cashier.read(Cashier)
            waiters = Waiter.read(Waiter)
            return render_template("manager/orders.html", mod=module, orders=orders, total_bill=total_bill,
                                   total_paid=total_paid, cashiers=cashiers, waiters=waiters)


@order.route("/filter", methods=["GET"])
@login_required
def filter_orders():
    if request.method == "GET":
        cashiers = Cashier.read(Cashier)
        waiters = Waiter.read(Waiter)
        
        cashier = request.args.get("cashier")
        if not cashier and current_user.cashier:
            cashier = str(current_user.cashier.id)
        elif not cashier and not current_user.cashier:
            cashier = ""

        open = request.args.get("open")

        waiter = request.args.get("waiter")
        if not waiter:
            waiter = ""
        _from = request.args["from"]
        to = request.args["to"]

        if _from:
            _from = utils.convert_date_from_html(_from)
        else:
            _from = datetime.datetime(2000,1,1)
        if to:
            to = utils.convert_date_from_html(to)
        else:
            to = datetime.datetime(3000,1,1)

        orders = Order.filter(Order, open, cashier, waiter, _from, to)

        # Avoid error on changing str to int
        if cashier == "":
            cashier = 0
        if waiter == "":
            waiter = 0

        total_bill, total_paid = utils.compute_total_bill_and_total_paid_from_orders(orders)

        if current_user.manager:  
            return render_template("manager/orders.html", mod=module, orders=orders, total_bill=total_bill, total_paid=total_paid, cashiers=cashiers, waiters=waiters, cashier_id=int(cashier), waiter_id=int(waiter), today=_from, tomorrow=to)
        elif current_user.cashier:
            return render_template("cashier/orders.html", mod=module, orders=orders, total_bill=total_bill, total_paid=total_paid, cashiers=cashiers, waiters=waiters, cashier_id=int(cashier), waiter_id=int(waiter), today=_from, tomorrow=to)


@order.route("/<id>", methods=["GET"])
@login_required
def get_order(id):
    if request.method == "GET":
        order = Order.read_one(Order, id)
        if current_user.manager:
            cashiers = Cashier.read(Cashier)
            waiters = Waiter.read(Waiter)
            return render_template("manager/order.html", mod=module, order=order, waiters=waiters, cashiers=cashiers)
        elif current_user.cashier:
            return render_template("cashier/order.html", mod=module, order=order)
        elif current_user.chef:
            return render_template("chef/order.html", mod=module, order=order)


@order.route("add-payment/<id>", methods=["POST"])
@login_required
def add_payment(id):
    if request.method == "POST":
        order_id = request.form["order"]
        payment = request.form["payment-added"]
        order = Order.read_one(Order, order_id)
        if int(payment) > (order.bill-order.paid) or int(payment) < 0:
            flash("Invalid Payment", "danger")
        else:
            order.update_payment(int(payment))
            flash("Payment added sucessfully", "success")
        return redirect(url_for('order.get_order', id=id))


@order.route("/settle-payment/<id>", methods=["GET"])
@login_required
def settle_payment(id):
    if request.method == "GET":
        order = Order.read_one(Order, id=id)
        balance = order.bill - order.paid
        if balance < 0:
            order.paid = order.bill
            session.commit()
        else:
            flash("Error occured! Please try again.", "danger")
        return redirect(url_for('order.get_order', id=id))


@order.route("/edit/<id>", methods=["GET", "POST"])
def edit_order(id):
    if request.method == "GET":
        order = Order.read_one(Order, id)
        if order.open:
            # get drink categories dict
            drink_categories = Category.read(Category)
            # get food categories dict
            food_categories = FoodCategory.read(FoodCategory)
            # get_order

            sold_items = {"food_items": {}, "drink_items": {}}
            for sale in order.sales:
                if sale.food_id:
                    sold_items["food_items"][sale.food_id] = sale.quantity
                elif sale.brand_id:
                    sold_items["drink_items"][sale.brand_id] = [sale.sale_guide_id, sale.quantity]

            return render_template('cashier/edit-order.html', order_id=id, categories=drink_categories,
                                   food_categories=food_categories, order=order, sold_items=sold_items, mod=module)
        return redirect(url_for('order.get_order', id=id))

    elif request.method == "POST":
        order = Order.read_one(Order, id)
        old_sales = order.sales
        for sale in old_sales:
            sale_quantity = sale.quantity
            sale_guide = SaleGuide.read_one(SaleGuide, id=sale.sale_guide_id)
            if sale_guide:
                # convert to sale_quantity to purchase unit
                purchase_unit_quantity = sale_quantity/sale_guide.quantity_in_purchase_unit
                brand = Brand.read_one(Brand, id=sale.brand_id)
                brand.update_quantity(purchase_unit_quantity)
            else:
                units = sale.quantity
                food = Food.read_one(Food, id=sale.food_id)
                food.update_units(units)

            # delete the sale
            session.delete(sale)
            session.commit()

        sales = request.form["sales"]
        sales = json.loads(sales)
        food_sales = sales["food_items"]
        drink_sales = sales["drink_items"]

        verified_bill = 0

        for drink_sale in drink_sales.values():
            brand = Brand.read_one(Brand, drink_sale["id"])
            sale_guide = SaleGuide.read_one(SaleGuide, id=drink_sale["sale_guide_id"])
            reduce_quantity = float(drink_sale["quantity"]) / float(sale_guide.quantity_in_purchase_unit)
            Sale(drink_sale["sale_unit"], drink_sale["sale_price"], drink_sale["quantity"], order, order.waiter,
                 order.cashier, brand=brand, reduce_quantity=reduce_quantity, sale_guide_id=drink_sale["sale_guide_id"])
            verified_bill += int(drink_sale["quantity"]) * int(drink_sale["sale_price"])

        for food_sale in food_sales.values():
            food = Food.read_one(Food, food_sale["id"])
            reduce_quantity = float(food_sale["quantity"])
            Sale(food_sale["sale_unit"], food_sale["sale_price"], food_sale["quantity"], order, order.waiter, order.cashier,
                 food=food, reduce_quantity=reduce_quantity)
            verified_bill += int(food_sale["quantity"]) * int(food_sale["sale_price"])

        order.bill = verified_bill
        session.commit()
        return redirect(url_for('order.get_order', id=id))


@order.route("/edit-order-info/<id>", methods=["POST"])
@login_required
def edit_order_info(id):
    if request.method == "POST":
        order = Order.read_one(Order, id)
        if order.open:
            cashier_id = request.form['cashier']
            customer = request.form['customer']
            waiter_id = request.form['waiter']
            paid = request.form['paid']
            if int(paid) > order.bill:
                flash("Invalid Payment", "danger")
                return redirect(url_for('order.get_order', id=id))
            cashier = Cashier.read_one(Cashier, cashier_id)
            waiter = Waiter.read_one(Waiter, waiter_id)
            order.update_info(cashier, waiter, customer, paid)
            flash("Order info was edited successfully", "success")
        return redirect(url_for('order.get_order', id=id))


@order.route("/close_order/<id>", methods=["POST"])
@login_required
def close_order(id):
    if request.method == "POST":
        order = Order.read_one(Order, id)
        order.close()
        flash("Order "+order.order_ref+" has been closed successfully", "info")
    return redirect(url_for('order.get_order', id=id))


@order.route("/open_order/<id>", methods=["POST"])
@login_required
def open_order(id):
    if request.method == "POST":
        order = Order.read_one(Order, id)
        order._open()
        flash("Order "+order.order_ref+" has been opened", "info")
    return redirect(url_for('order.get_order', id=id))


@order.route("/get-edit-order-data/<id>", methods=["GET"])
@login_required
def get_edit_order_data(id):
    data = dict()
    foods = Food.read(Food)
    drinks = Brand.read(Brand)
    # get sale items dict
    sale_items_dict = utils.build_sale_items_dict(foods, drinks)
    data["sale_items"] = sale_items_dict
    # get order dict
    order = Order.read_one(Order, id)
    order_dict = utils.build_order_dict(order)
    data["order"] = order_dict
    return jsonify(data)