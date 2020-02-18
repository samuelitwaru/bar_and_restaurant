from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import current_user, login_required
from Application.blueprints import utils
import datetime
from Application.database.model import Chef, KitchenStockPurchase, KitchenStock, session

kitchen_stock_purchase = Blueprint('kitchen_stock_purchase', __name__, url_prefix="/kitchen-stock-purchase")


module = kitchen_stock_purchase.name


@kitchen_stock_purchase.route("/")
@login_required
def get_kitchen_stock_purchases():
    kitchen_stock_purchases = KitchenStockPurchase.read(KitchenStockPurchase)
    chefs = Chef.read(Chef)
    kitchen_items = KitchenStock.read(KitchenStock)
    if current_user.manager:
        return render_template("manager/kitchen-stock-purchase.html", mod=module, purchases=kitchen_stock_purchases, chefs=chefs, kitchen_items=kitchen_items)
    elif current_user.chef:
        return render_template("chef/kitchen-stock-purchase.html", mod=module, purchases=kitchen_stock_purchases, chefs=chefs, kitchen_items=kitchen_items)


@kitchen_stock_purchase.route("/filter", methods=["GET"])
@login_required
def filter():
    if request.method == "GET":
        item = request.args.get("item")
        chef = request.args.get("chef")
        _from = request.args.get("from")
        to = request.args.get("to")

        if not item: item = ""
        if not chef: chef = ""

        if _from:
            _from = utils.convert_date_from_html(_from)
        else:
            _from = datetime.datetime(2000, 1, 1)
        if to:
            to = utils.convert_date_from_html(to)
        else:
            to = datetime.datetime(3000, 1, 1)

        kitchen_stock_purchases = KitchenStockPurchase.filter(KitchenStockPurchase, item, chef, _from, to)
        chefs = Chef.read(Chef)
        kitchen_items = KitchenStock.read(KitchenStock)

        if current_user.manager:
            return render_template("manager/kitchen-stock-purchase.html", mod=module, purchases=kitchen_stock_purchases,
                                   chefs=chefs, kitchen_items=kitchen_items, chef_id=chef, item_id=item, today=_from, tomorrow=to)
        elif current_user.chef:
            return render_template("chef/kitchen-stock-purchase.html", mod=module, purchases=kitchen_stock_purchases,
                                   chefs=chefs, kitchen_items=kitchen_items, chef_id=chef, item_id=item, today=_from, tomorrow=to)

