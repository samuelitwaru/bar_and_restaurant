from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import current_user, login_required
from Application.database.model import KitchenStock, KitchenStockUsage, KitchenStockPurchase, session

kitchen_stock = Blueprint('kitchen_stock', __name__, url_prefix="/kitchen-stock")

module = kitchen_stock.name


@kitchen_stock.route("/")
@login_required
def get_kitchen_stock():
    all_kitchen_stock = KitchenStock.read(KitchenStock)
    if current_user.manager:
        return render_template("manager/kitchen-stock.html", mod=module, all_kitchen_stock = all_kitchen_stock)
    elif current_user.chef:
        return render_template("chef/kitchen-stock.html", mod=module, all_kitchen_stock = all_kitchen_stock)


@kitchen_stock.route("/add", methods=["POST"])
@login_required
def add_kitchen_stock():
    if request.method == "POST":
        name = request.form["kitchen-item"]
        usage_unit = request.form["usage-unit"]
        KitchenStock(name, usage_unit)
        session.close()
        flash(name+" has been registered as Kitchen Stock", "success")
        return redirect(url_for('kitchen_stock.get_kitchen_stock'))


@kitchen_stock.route("/edit", methods=["POST", "GET"])
@login_required
def edit_kitchen_stock():
    if request.method == "POST":
        kitchen_stock_id = request.form["kitchen-stock"]
        name = request.form["kitchen-item"]
        usage_unit = request.form["usage-unit"]
        stock = KitchenStock.read_one(KitchenStock, kitchen_stock_id)
        stock.update(name, usage_unit)
        session.close()
        flash("Item has been edited", "success")
        return redirect(url_for('kitchen_stock.get_kitchen_stock'))
    elif request.method == "GET":
        kitchen_stock_id = request.args["kitchen-stock"]
        stock = KitchenStock.read_one(KitchenStock, kitchen_stock_id)
        if current_user.manager:
            return render_template("manager/edit-kitchen-stock.html", mod=module, stock=stock)
        elif current_user.chef:
            return render_template("chef/edit-kitchen-stock.html", mod=module, stock=stock)


@kitchen_stock.route("/delete", methods=["POST"])
@login_required
def delete_kitchen_stock():
    if request.method == "POST":
        kitchen_stock_id = request.form["kitchen-stock"]
        stock = KitchenStock.read_one(KitchenStock, kitchen_stock_id)
        KitchenStock.delete(stock)
        flash("Item has been deleted", "info")
        session.close()
        return redirect(url_for('kitchen_stock.get_kitchen_stock'))


@kitchen_stock.route("/add-stock", methods=["POST", "GET"])
@login_required
def add_stock():
    if request.method == "POST":
        added_stock_quantity = request.form['added-stock-quantity']
        stock_id = request.form['stock']
        stock = KitchenStock.read_one(KitchenStock, stock_id)

        try:
            if int(added_stock_quantity) < 1:
                flash("Invalid Stock Added!", 'danger')
                return redirect(url_for('kitchen_stock.add_stock') + '?kitchen-stock='+stock_id)
            else:
                # record purchase
                purchase_unit = request.form['purchase-unit']
                unit_price = request.form['unit-price']
                purchase_quantity = request.form['purchase-quantity']
                KitchenStockPurchase(purchase_unit, unit_price, purchase_quantity, added_stock_quantity, stock.usage_unit, current_user, stock)
                flash("Registered Purchase of "+ stock.name +" successfully", 'success')
                session.close()
                return redirect(url_for('kitchen_stock.get_kitchen_stock'))
        except ValueError:
            flash("Invalid Stock Added!", 'danger')
            return redirect(url_for('kitchen_stock.add_stock') + '?kitchen-stock=' + stock_id)

    elif request.method == "GET":
        stock_id = request.args['kitchen-stock']
        stock = KitchenStock.read_one(KitchenStock, stock_id)
        if current_user.manager:
            return render_template("manager/add-kitchen-stock.html", mod=module, stock=stock)
        elif current_user.chef:
            return render_template("chef/add-kitchen-stock.html", mod=module, stock=stock)


@kitchen_stock.route("/reduce-kitchen-stock", methods=["POST", "GET"])
@login_required
def reduce_kitchen_stock():
    if request.method == "POST":
        quantity = request.form['quantity']
        stock_id = request.form['stock']
        stock = KitchenStock.read_one(KitchenStock, stock_id)
        try:
            if int(quantity) < 1:
                flash("Invalid Input!", 'danger')
            else:
                stock.add_quantity(0-int(quantity))
                flash("Reduced "+quantity+" units of "+stock.name+" from kitchen stock", 'info')
                session.close()
                return redirect(url_for('kitchen_stock.get_kitchen_stock'))
        except Exception as e:
            flash("Invalid Input!", 'danger')
        return redirect(url_for('kitchen_stock.reduce_stock')+'?kitchen-stock='+stock_id)
    else:
        stock_id = request.args['kitchen-stock']
        stock = KitchenStock.read_one(KitchenStock, stock_id)
        return render_template("manager/reduce-kitchen-stock.html", mod=module, stock=stock)


@kitchen_stock.route("/register-usage", methods=["POST", "GET"])
@login_required
def register_usage():
    if request.method == "POST":
        kitchen_stock_id = request.form.get("kitchen-stock")
        quantity_used = float(request.form.get("quantity"))
        stock = KitchenStock.read_one(KitchenStock, kitchen_stock_id)

        if stock.quantity_available >= quantity_used or quantity_used < 0:
            chef = current_user.chef
            stock.kitchen_stock_usages.append(KitchenStockUsage(stock, quantity_used, chef))
            stock.reduce_quantity(quantity_used)
            flash("Stock usage registered", "info")
            return redirect(url_for('kitchen_stock.get_kitchen_stock'))
        else:
            flash("Invalid input", "danger")
            return redirect(url_for('kitchen_stock.register_usage')+"?kitchen-stock="+kitchen_stock_id)
    elif request.method == "GET":
        kitchen_stock_id = request.args.get("kitchen-stock")
        kitchen_stock = KitchenStock.read_one(KitchenStock, kitchen_stock_id)
        return render_template("chef/register-kitchen-stock-usage.html", mod=module, stock = kitchen_stock)















