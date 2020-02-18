from flask import Blueprint, render_template, request, redirect, url_for
from Application.database.model import FoodCategory
from flask_login import login_required, current_user

food_category = Blueprint('food_category', __name__, url_prefix="/food-category")


module = food_category.name


@food_category.route("/")
@login_required
def get_categories():
    categories = FoodCategory.read(FoodCategory)
    if current_user.manager:
        return render_template("manager/food-categories.html", mod=module, categories=categories)
    elif current_user.chef:
        return render_template("chef/food-categories.html", mod=module, categories=categories)


@food_category.route("/add", methods=["POST"])
@login_required
def add_category():
    category_name = request.form["category"]
    FoodCategory(category_name)
    return redirect(url_for('food_category.get_categories'))


@food_category.route("/update", methods=["POST"])
@login_required
def update_category():
    category_id = request.form["category-id"]
    category_name = request.form["category"]
    c = FoodCategory.read_one(FoodCategory, category_id)
    FoodCategory.update(c, category_name)
    return redirect(url_for('food_category.get_categories'))


@food_category.route("/delete", methods=["POST"])
@login_required
def delete_category():
    category_id = request.form["category-id"]
    c = FoodCategory.read_one(FoodCategory, category_id)
    FoodCategory.delete(c)
    return redirect(url_for('food_category.get_categories'))
