from flask import Blueprint, render_template, url_for, request, redirect, flash
from Application.database.model import Brand, Category, PurchaseGuide, SaleGuide, Purchase, session
from flask_login import login_required

brand = Blueprint('brand', __name__, url_prefix="/brand")
module = brand.name


@brand.route("/")
@login_required
def get_brands():
    brands = Brand.read(Brand)
    categories = Category.read(Category)
    return render_template("manager/brands.html", mod=module, brands=brands, categories=categories)


@brand.route("/add", methods=["POST"])
@login_required
def add_brand():
    if request.method == "POST":
        brand_name = request.form["brand"]
        category_id = request.form["category"]
        purchase_unit = request.form["purchase-unit"]
        purchase_price = request.form["purchase-price"]
        category = Category.read_one(Category, category_id)
        purchase_guide = PurchaseGuide(purchase_unit, purchase_price)
        Brand(brand_name, 0, category, purchase_guide)
        session.close()
        return redirect(url_for('brand.get_brands'))


@brand.route("/edit", methods=["POST", "GET"])
@login_required
def edit_brand():
    if request.method == "POST":
        category_id = request.form["category"]
        brand_id = request.form["brand-id"]
        brand_name = request.form["brand"]
        purchase_unit = request.form["purchase-unit"]
        purchase_price = request.form["purchase-price"]
        c = Category.read_one(Category, category_id)
        b = Brand.read_one(Brand, brand_id)
        pg = PurchaseGuide.read_one(PurchaseGuide, b.purchase_guide_id)
        Brand.update(b, brand_name, c)
        pg.update(purchase_unit, purchase_price)
        session.close()
        return redirect(url_for('brand.get_brands'))
    else:
        brand_id = request.args["brand"]
        brand = Brand.read_one(Brand, brand_id)
        categories = Category.read(Category)
        return render_template("manager/edit-brand.html", mod=module, brand=brand, categories=categories)


@brand.route("/delete", methods=["POST"])
@login_required
def delete_brand():
    brand_id = request.form["brand-id"]
    b = Brand.read_one(Brand, brand_id)
    Brand.delete(b)
    session.close()
    return redirect(url_for('brand.get_brands'))


@brand.route("/sale-guides", methods=["POST", "GET"])
@login_required
def sale_guides():
    if request.method == "POST":
        unit = request.form["sale-unit"]
        price = request.form["sale-price"]
        quantity_in_purchase_unit = request.form["quantity-in-purchase-unit"]
        brand_id = request.form['brand']
        brand = Brand.read_one(Brand, brand_id)
        SaleGuide(unit, price, quantity_in_purchase_unit, brand)
        session.close()
        return redirect('/brand/sale-guides?brand=' + str(brand_id))
    else:
        brand_id = request.args["brand"]
        brand = Brand.read_one(Brand, brand_id)
        return render_template("manager/sale-guides.html", mod=module, brand=brand)


@brand.route("/delete-sale-guide", methods=["POST"])
@login_required
def delete_sale_guide():
    sale_guide_id = request.form["sale-guide-id"]
    sg = SaleGuide.read_one(SaleGuide, sale_guide_id)
    brand_id = sg.brand.id
    SaleGuide.delete(sg)
    session.close()
    return redirect('/brand/sale-guides?brand=' + str(brand_id))


@brand.route("/add-stock", methods=["POST", "GET"])
@login_required
def add_stock():
    if request.method == "POST":
        quantity = request.form['quantity']
        brand_id = request.form['brand']
        brand = Brand.read_one(Brand, brand_id)
        try:
            if int(quantity) < 1:
                flash("Invalid Input!", 'danger')
            else:
                brand.add_quantity(quantity)
                Purchase(brand.purchase_guide.purchase_unit, brand.purchase_guide.purchase_price, quantity, brand)
                flash("Added "+quantity+" units of "+brand.name+" successfully", 'success')
                session.close()
                return redirect(url_for('brand.get_brands'))
        except Exception as e:
            flash("Invalid Input!", 'danger')
        return redirect(url_for('brand.add_stock')+'?brand='+brand_id)
    else:
        brand_id = request.args["brand"]
        brand = Brand.read_one(Brand, brand_id)
        return render_template("manager/add-stock.html", mod=module, brand=brand)


@brand.route("/reduce-stock", methods=["POST", "GET"])
@login_required
def reduce_stock():
    if request.method == "POST":
        quantity = request.form['quantity']
        brand_id = request.form['brand']
        brand = Brand.read_one(Brand, brand_id)
        try:
            if int(quantity) < 1:
                flash("Invalid Input!", 'danger')
            else:
                brand.add_quantity(0-int(quantity))
                flash("Reduced "+quantity+" units of "+brand.name+" from stock", 'info')
                session.close()
                return redirect(url_for('brand.get_brands'))
        except Exception as e:
            flash("Invalid Input!", 'danger')
        return redirect(url_for('brand.reduce_stock')+'?brand=1')
    else:
        brand_id = request.args["brand"]
        brand = Brand.read_one(Brand, brand_id)
        return render_template("manager/reduce-stock.html", mod=module, brand=brand)


@brand.route("/filter", methods=["GET"])
@login_required
def filter():
    if request.method == "GET":
        category_id = request.args['category']
        if category_id == "All":
            return redirect(url_for('brand.get_brands'))
        else:
            categories = Category.read(Category)
            brands = session.query(Brand).filter_by(category_id=category_id)
            return render_template("manager/brands.html", mod=module, brands=brands, categories=categories)
