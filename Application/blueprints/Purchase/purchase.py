from flask import Blueprint, render_template, url_for, request, redirect, flash
from Application.database.model import KitchenStockPurchase, KitchenStock, Brand, Purchase, session
from flask_login import login_required
from Application.blueprints import utils
import datetime

purchase = Blueprint('purchase', __name__, url_prefix="/purchase")

module = purchase.name


@purchase.route("/")
@login_required
def get_purchases():
    kitchen_purchases = KitchenStockPurchase.read(KitchenStockPurchase)
    kitchen_items = KitchenStock.read(KitchenStock)
    drink_items = Brand.read(Brand)
    brand_purchases = Purchase.read(Purchase)

    total_purchases = KitchenStockPurchase.get_total_price(KitchenStockPurchase) + Purchase.get_total_price(Purchase)
    return render_template("manager/purchases.html", mod=module, total_purchases=total_purchases, kitchen_purchases=kitchen_purchases, kitchen_items=kitchen_items, drink_items=drink_items, brand_purchases=brand_purchases)


@purchase.route("/filter", methods=["GET"])
@login_required
def filter():
    if request.method == "GET":
        kitchen_items = KitchenStock.read(KitchenStock)
        drink_items = Brand.read(Brand)

        kitchen_purchases = []
        brand_purchases = []

        item = request.args.get("item")
        _from = request.args.get("from")
        to = request.args.get("to")
        place = request.args.get("place")
        filter_kitchen, filter_bar = True, True
        if place == "kitchen": filter_bar = False
        elif place == "bar": filter_kitchen = False

        if _from:
            _from = utils.convert_date_from_html(_from)
        else:
            _from = datetime.datetime(2000, 1, 1)
        if to:
            to = utils.convert_date_from_html(to)
        else:
            to = datetime.datetime(3000, 1, 1)

        if item:
            item_type, id = item.split("-")
            if item_type == "kitchen":
                kitchen_purchases = KitchenStockPurchase.filter2(KitchenStockPurchase, id, _from, to, filter_kitchen)
            elif item_type == "drink":
                brand_purchases = Purchase.filter(Purchase, id, _from, to, filter_bar)
        else:
            kitchen_purchases = KitchenStockPurchase.filter2(KitchenStockPurchase, "", _from, to, filter_kitchen)
            brand_purchases = Purchase.filter(Purchase, "", _from, to, filter_bar)

        print(">>>>>>>>>>>>>>>>>", kitchen_purchases, brand_purchases)

        total_purchases = KitchenStockPurchase.get_total_price(KitchenStockPurchase, purchases=kitchen_purchases) + Purchase.get_total_price(Purchase, purchases=brand_purchases)

        return render_template("manager/purchases.html", mod=module, kitchen_purchases=kitchen_purchases, total_purchases=total_purchases, kitchen_items=kitchen_items, drink_items=drink_items, item_id=item, brand_purchases=brand_purchases, tomorrow=to, today=_from)


@purchase.route('/delete-purchase', methods=["POST"])
@login_required
def delete_purchase():
    purchase_id = request.form["purchase-id"]
    purchase = Purchase.read_one(Purchase, purchase_id)
    Purchase.delete(purchase)
    session.close()
    flash("Purchase ("+ purchase_id +") was deleted successfully", "info")
    return redirect(url_for('purchase.get_purchases'))


@purchase.route('/delete-kitchen-purchase', methods=["POST"])
@login_required
def delete_kitchen_purchase():
    purchase_id = request.form["kitchen-purchase-id"]
    purchase = KitchenStockPurchase.read_one(KitchenStockPurchase, purchase_id)
    KitchenStockPurchase.delete(purchase)
    session.close()
    flash("Kitchen Purchase ("+ purchase_id +") was deleted successfully", "info")
    return redirect(url_for('purchase.get_purchases'))