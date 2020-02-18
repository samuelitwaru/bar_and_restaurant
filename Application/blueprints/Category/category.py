from flask import Blueprint, render_template, request, redirect, url_for
from Application.database.model import Category
from flask_login import login_required

category = Blueprint('category', __name__, url_prefix="/category")

module = category.name


@category.route("/")
@login_required
def get_categories():
    categories = Category.read(Category)
    return render_template("manager/categories.html", mod=module, categories=categories)


@category.route("/add", methods=["POST"])
@login_required
def add_category():
    category_name = request.form["category"]
    Category(category_name)
    return redirect(url_for('category.get_categories'))


@category.route("/update", methods=["POST"])
@login_required
def update_category():
    category_id = request.form["category-id"]
    category_name = request.form["category"]
    c = Category.read_one(Category, category_id)
    Category.update(c, category_name)
    return redirect(url_for('category.get_categories'))


@category.route("/delete", methods=["POST"])
@login_required
def delete_category():
    category_id = request.form["category-id"]
    c = Category.read_one(Category, category_id)
    Category.delete(c)
    return redirect(url_for('category.get_categories'))