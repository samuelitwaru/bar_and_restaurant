from flask import Blueprint, render_template, url_for, request, redirect, flash
from Application.database.model import Email, Sale, Purchase
import datetime
from flask_login import current_user, login_required
from flask_mail import Message
from Application import mail
from Application.blueprints import utils


email = Blueprint('email', __name__, url_prefix="/email")


@email.route("/send-email")
@login_required
def send_email():
    # check the last time an email was sent. if the duration is
    # above 7 days, then send an email. else do nothing
    latest_email, date = Email.get_latest(Email)
    duration = datetime.timedelta(0)
    if latest_email:
        today = datetime.datetime.now()
        duration = today - date
    if duration > datetime.timedelta(7):
        # get sales and purchases
        sales = Sale.filter(Sale, "all", "", "", date, datetime.datetime(9999, 12, 31))
        total_sales = utils.compute_sales(sales)
        purchases = Purchase.filter(Purchase, "", date, datetime.datetime(9999, 12, 31))
        total_purchases = utils.compute_purchases(purchases)
        # get boss' email address
        boss_email = current_user.manager.boss_email
        # send email
        msg = Message("Weekly sales and purchases", sender='samuelitwaru@gmail.com', recipients=[boss_email])
        msg.html = render_template('manager/sales_and_purchases_email.html', sales=sales, purchases=purchases, total_sales=total_sales, total_purchases=total_purchases, date=date)
        try:
            mail.send(msg)
            Email()
            # return render_template('manager/sales_and_purchases_email.html', sales=sales, purchases=purchases, total_sales=total_sales, total_purchases=total_purchases, date=date)
        except:
            pass
    return redirect(url_for('user.login'))




