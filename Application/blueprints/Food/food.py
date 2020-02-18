from flask import Blueprint, render_template, url_for, request, redirect, flash
from Application.database.model import Food, FoodCategory, SaleGuide, Purchase, session
from flask_login import login_required

food = Blueprint('food', __name__, url_prefix="/food")

module = food.name


@food.route("/")
@login_required
def get_foods():
    foods = Food.read(Food)
    categories = FoodCategory.read(FoodCategory)
    return render_template("manager/foods.html", mod=module, foods=foods, categories=categories)


@food.route("/add", methods=["POST"])
@login_required
def add_food():
    if request.method == "POST":
        food_name = request.form["food"]
        category_id = request.form["category"]
        sale_unit = request.form["sale-unit"]
        sale_price = request.form["sale-price"]
        category = FoodCategory.read_one(FoodCategory, category_id)
        Food(food_name, 0, sale_unit, sale_price, category)
        session.close()
        return redirect(url_for('food.get_foods'))


@food.route("/edit", methods=["POST", "GET"])
@login_required
def edit_food():
    if request.method == "POST":
        category_id = request.form["category"]
        food_id = request.form["food-id"]
        food_name = request.form["food"]
        sale_unit = request.form["sale-unit"]
        sale_price = request.form["sale-price"]
        c = FoodCategory.read_one(FoodCategory, category_id)
        f = Food.read_one(Food, food_id)
        Food.update(f, food_name, sale_unit, sale_price, c)
        session.close()
        return redirect(url_for('food.get_foods'))
    else:
        food_id = request.args["food"]
        food = Food.read_one(Food, food_id)
        categories = FoodCategory.read(FoodCategory)
        return render_template("manager/edit-food.html", mod=module, food = food, categories=categories)


@food.route("/delete", methods=["POST"])
@login_required
def delete_food():
    food_id = request.form["food-id"]
    b = Food.read_one(Food, food_id)
    Food.delete(b)
    session.close()
    return redirect(url_for('food.get_foods'))


@food.route("/sale-guides", methods=["POST", "GET"])
@login_required
def sale_guides():
    if request.method == "POST":
        unit = request.form["sale-unit"]
        price = request.form["sale-price"]
        quantity_in_purchase_unit = request.form["quantity-in-purchase-unit"]
        food_id = request.form['food']
        food = Food.read_one(Food, food_id)
        SaleGuide(unit, price, quantity_in_purchase_unit, food)
        session.close()
        return redirect('/food/sale-guides?food=' + str(food_id))
    else:
        food_id = request.args["food"]
        food = Food.read_one(Food, food_id)
        return render_template("manager/sale-guides.html", mod=module, food=food)


@food.route("/delete-sale-guide", methods=["POST"])
@login_required
def delete_sale_guide():
    sale_guide_id = request.form["sale-guide-id"]
    sg = SaleGuide.read_one(SaleGuide, sale_guide_id)
    food_id = sg.food.id
    SaleGuide.delete(sg)
    session.close()
    return redirect('/food/sale-guides?food=' + str(food_id))


@food.route("/add-stock", methods=["POST", "GET"])
@login_required
def add_stock():
    if request.method == "POST":
        quantity = request.form['quantity']
        food_id = request.form['food']
        food = Food.read_one(Food, food_id)
        food.add_quantity(quantity)
        Purchase(food.purchase_guide.purchase_unit, food.purchase_guide.purchase_price, quantity, food)
        session.close()
        return redirect(url_for('food.get_foods'))
    else:
        food_id = request.args["food"]
        food = Food.read_one(Food, food_id)
        session.close()
        return render_template("manager/add-stock.html", mod=module, food=food)


@food.route("/filter", methods=["GET"])
@login_required
def filter():
    if request.method == "GET":
        category_id = request.args['category']
        if category_id == "All":
            return redirect(url_for('food.get_foods'))
        else:
            categories = FoodCategory.read(FoodCategory)
            foods = session.query(Food).filter_by(category_id=category_id)
            return render_template("manager/foods.html", mod=module, foods=foods, categories=categories)


@food.route("/food-menu")
@login_required
def food_menu():
    foods = Food.read(Food)
    categories = FoodCategory.read(FoodCategory)
    return render_template("chef/food-menu.html", foods=foods, mod=module, categories=categories)


@food.route("/filter_food_menu", methods=["GET"])
@login_required
def filter_food_menu():
    if request.method == "GET":
        category_id = request.args['category']
        if category_id == "All":
            return redirect(url_for('food.food_menu'))
        else:
            categories = FoodCategory.read(FoodCategory)
            foods = session.query(Food).filter_by(category_id=category_id)
            return render_template("chef/food-menu.html", mod=module, foods=foods, categories=categories)


@food.route("/update-units", methods=["GET", "POST"])
@login_required
def update_food_units():
    if request.method == "POST":
        food_id = request.form["food-id"]
        units = request.form["units"]
        if float(units) < 0:
            flash("Units cannot be less than 0", "info")
            return redirect('/food/update-units?food='+food_id)
        food = Food.read_one(Food, food_id)
        Food.update_units(food, units)
        flash("Added "+str(units)+" units of "+food.name, "info")
        session.close()
        return redirect(url_for('food.food_menu'))
    elif request.method == "GET":
        food_id = request.args["food"]
        food = Food.read_one(Food, food_id)
        categories = FoodCategory.read(FoodCategory)
        return render_template("chef/update-food-units.html", mod=module, food = food, categories=categories)
