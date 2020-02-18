from flask import Blueprint, request, url_for, redirect, render_template
from Application.database.model import PurchaseGuide, Brand
from flask_login import login_required

purchase_guide = Blueprint('purchase_guide',__name__, url_prefix="/purchase-guide")

module = purchase_guide.name


@purchase_guide.route("/add", methods=["POST"])
@login_required
def add_purchase_guide():
    unit = request.form["purchase-unit"]
    price = request.form["purchase-price"]
    brand_id = request.form['brand-id']
    brand = Brand.read_one(Brand, brand_id)
    PurchaseGuide(unit, price, brand)
    return redirect(url_for('brand.get_brands'))


@purchase_guide.route("/delete", methods=["POST"])
@login_required
def delete_purchase_guide():
    purchase_guide_id = request.form["purchase-guide-id"]
    pg = PurchaseGuide.read_one(PurchaseGuide, purchase_guide_id)
    PurchaseGuide.delete(pg)
    return redirect(url_for('brand.get_brands'))