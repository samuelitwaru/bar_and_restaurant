from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from Application.database.model import User, Session, Manager, session

user = Blueprint('user', __name__, url_prefix="/")

module = user.name


@user.route("/", methods=["POST", "GET"])
@user.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.find_user(User, username, password)
        if user:
            role = user.get_role()
            if role == "cashier":
                if not Session.get_current_session(Session, user.cashier):
                    login_user(user, True)
                    Session(user.cashier)
                    return redirect(url_for('user.login'))
                else:
                    flash("You are logged in another location. Please logout before logging in again", "info")
                    session.close()
                    return redirect(url_for('user.login'))
            elif role == "manager":
                login_user(user, True)
                session.close()
                return redirect(url_for('email.send_email'))
            elif role == "chef":
                login_user(user, True)
                session.close()
                return redirect(url_for('sale.get_food_sales'))
            flash("User not found", "danger")
            session.close()
            return redirect(url_for('user.login'))
        else:
            flash("User not found", "danger")
            session.close()
            return redirect(url_for('user.login'))
    elif request.method == "GET":
        if current_user.is_authenticated:
            if current_user.cashier_id:
                session.close()
                return redirect(url_for('order.get_orders'))
            elif current_user.manager_id:
                session.close()
                return redirect(url_for('sale.get_sales'))
            elif current_user.chef_id:
                session.close()
                return redirect(url_for('sale.get_food_sales'))
        else:
            managers = Manager.read(Manager)
            manager_available = True
            if len(managers) == 0:
                manager_available = False
            session.close()
            return render_template('global/login.html',  mod=module, manager_available=manager_available)


@user.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))