from datetime import datetime
import random
import string
from Application.database.model import Brand

def convert_date_from_html(html_date_string):
    """Converts dates got from html forms"""
    yy,mm,dd = html_date_string.split("-")
    return datetime(int(yy),int(mm),int(dd))


def compute_sales(sales):
    """Calculate the total sales for a group of sales passed"""
    total = 0
    for sale in sales:
        total += (sale.sale_price * sale.quantity)
    return total


def compute_total_bill_and_total_paid_from_orders(orders):
    """Calculate the total sales for a group of sales passed"""
    total_bill = 0
    total_paid = 0
    for order in orders:
        total_paid += order.paid
        sales = order.sales
        for sale in sales:
            total_bill += (sale.sale_price * sale.quantity)
    return total_bill, total_paid


def compute_purchases(purchases):
    """Caluculate the total purchases for a group of purchases passed"""
    total = 0
    for purchase in purchases:
        total += purchase.purchase_price * purchase.quantity
    return total


def randomString(stringLength=12):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))


def build_sale_items_dict(foods, drinks):
    sale_items = {"food_items": {}, "drink_items": {}}
    for food in foods:
        sale_items["food_items"][food.food_ref] = {
            "id": food.id,
            "name": food.name,
            "category_id": food.category_id,
            "quantity_available": food.units_available,
            "sale_unit": food.sale_unit,
            "sale_price": food.sale_price,
            "quantity_ratio": 1,
            "quantity_available_in_sale_units": food.units_available,
        }
    for drink in drinks:
        sale_items["drink_items"][drink.brand_ref] = {
            "id": drink.id,
            "name": drink.name,
            "category": drink.category_id,
            "quantity_available": drink.quantity_available,
            "sale_guides": {}
        }
        for sale_guide in drink.sale_guides:
            sale_items["drink_items"][drink.brand_ref]["sale_guides"][sale_guide.id] = {
                "sale_unit": sale_guide.sale_unit,
                "sale_price": sale_guide.sale_price,
                "quantity_ratio": sale_guide.quantity_in_purchase_unit,
                "quantity_available_in_sale_units": int(
                    sale_guide.quantity_in_purchase_unit * drink.quantity_available),
            }

    return sale_items


def build_order_dict(order):
    order_dict = dict()
    order_dict["id"] = order.id
    order_dict["ref"] = order.order_ref
    order_dict["waiter"] = order.waiter_id,
    order_dict["cashier"] = order.cashier_id,
    order_dict["sales"] = {"food_items": {}, "drink_items": {}}
    for sale in order.sales:
        if sale.food_id:
            order_dict["sales"]["food_items"][sale.food.food_ref] = {
                    "id": sale.food_id, "name": sale.food.name, "food_ref": sale.food.food_ref, "sale_price": sale.sale_price,
                    "sale_unit": sale.sale_unit, "quantity": sale.quantity, "sale_guide_id": sale.sale_guide_id
                }
        if sale.brand_id:
            order_dict["sales"]["drink_items"][sale.brand.brand_ref] = {
                    "id": sale.brand_id, "name": sale.brand.name, "brand_ref": sale.brand.brand_ref, "sale_price": sale.sale_price,
                    "sale_unit": sale.sale_unit, "quantity": sale.quantity, "sale_guide_id": sale.sale_guide_id
                }
    return order_dict


def build_categories_dict(categories):
    categories_list = []
    for category in categories:
        categories_list.append({
            "id": category.id, "name": category.name
        })
    return categories_list


class SoldBrand:
    id = None
    brand_ref = None
    name = None
    quantity_available = None
    category_id = None
    sale_guides = None
    sale = None

    def __init__(self, id, brand_ref, name, quantity_available, category_id, sale_guides, sale):
        self.id = id
        self.brand_ref = brand_ref
        self.name = name
        self.quantity_available = quantity_available
        self.category_id = category_id
        self.sale_guides = sale_guides
        self.sale = sale


class SoldFood:
    id = None
    food_ref = None
    name = None
    units_available = None
    sale_unit = None
    sale_price = None
    category_id = None
    sale = None

    def __init__(self, id, food_ref, name, units_available, category_id, sale_unit, sale_price, sale):
        self.id = id
        self.food_ref = food_ref
        self.name = name
        self.units_available = units_available
        self.category_id = category_id
        self.sale_unit = sale_unit
        self.sale_price = sale_price
        self.sale = sale