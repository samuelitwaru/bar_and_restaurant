from flask import Blueprint, redirect, url_for, request
from Application.database.model import SaleGuide, Brand
from flask_login import login_required

sale_guide = Blueprint('sale_guide',__name__, url_prefix="/sale-guide")

module = sale_guide.name


@sale_guide.route("/add", methods=["POST"])
@login_required
def add_sale_guide():
    unit = request.form["sale-unit"]
    price = request.form["sale-price"]
    quantity_in_purchase_unit = request.form["quantity-in-purchase-unit"]
    brand_id = request.form['brand-id']
    brand = Brand.read_one(Brand, brand_id)
    SaleGuide(unit, price, quantity_in_purchase_unit, brand)
    return redirect(url_for('brand.get_brands'))


@sale_guide.route("/delete", methods=["POST"])
@login_required
def delete_sale_guide():
    sale_guide_id = request.form["sale-guide-id"]
    pg = SaleGuide.read_one(SaleGuide, sale_guide_id)
    SaleGuide.delete(pg)
    return redirect(url_for('brand.get_brands'))