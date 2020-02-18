from flask import Blueprint, render_template, request, redirect, url_for, flash
from Application.database.model import Cashier, User, Session, session
from flask_login import login_required, current_user, logout_user

cashier = Blueprint('cashier', __name__, url_prefix="/cashier")

module = cashier.name


@cashier.route("/")
@login_required
def get_cashiers():
    cashiers = Cashier.read(Cashier)
    return render_template("manager/cashiers.html", mod=module, cashiers=cashiers)


@cashier.route("/add", methods=["POST"])
@login_required
def add_cashier():
    if request.method == "POST":
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        username = request.form["username"]
        password = request.form["password"]
        password1 = request.form["password-1"]
        if password != password1:
            flash('Passwords do not match!', "warning")
            return redirect(url_for('cashier.get_cashiers'))
        user = User(username, password)
        Cashier(first_name, last_name, user)
        session.close()
        
    return redirect(url_for('cashier.get_cashiers'))


@cashier.route("/edit", methods=["POST", "GET"])
@login_required
def edit_cashier():
    if request.method == "POST":
        cashier_id = request.form["cashier"]
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        username = request.form["username"]
        cashier = Cashier.read_one(Cashier, cashier_id)
        cashier.update(first_name, last_name, username)
        session.close()
        return redirect(url_for('cashier.get_cashiers'))

    elif request.method == "GET":
        cashier_id = request.args["cashier"]
        cashier = Cashier.read_one(Cashier, cashier_id)
        return render_template("manager/cashiers.html", mod=module, cashier_to_edit=cashier)


@cashier.route("/reset", methods=["POST"])
@login_required
def reset_password():
    if request.method == "POST":
        cashier_id = request.form["cashier"]
        password = request.form["password"]
        password1 = request.form["password-1"]
        if password != password1:
            flash('Passwords do not match!', "warning")
            cashier = Cashier.read_one(Cashier, cashier_id)
            return render_template("manager/cashiers.html", mod=module, cashier_to_edit=cashier)
        cashier = Cashier.read_one(Cashier, cashier_id)
        cashier.update_password(password)
        session.close()
        flash('Password changed successfully!', "success")
        return redirect(url_for('cashier.get_cashiers'))


@cashier.route("/delete", methods=["POST"])
@login_required
def delete_cashier():
    if request.method == "POST":
        cashier_id = request.form["cashier"]
        cashier = Cashier.read_one(Cashier, cashier_id)
        Cashier.delete(cashier)
        return redirect(url_for('cashier.get_cashiers'))


@cashier.route("/change-password", methods=["POST", "GET"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form["c-password"]
        new_password = request.form["n-password"]
        confirm_password = request.form["r-password"]

        user = User.find_user(User, current_user.username, current_password)
        if user:
            if new_password == confirm_password:
                user.cashier.update_password(new_password)
                flash("Passsword resset successfully", "success")
            else:
               flash("Passwords do not match", "danger")
        else:
            flash("Incorrect current password", "danger")
        session.close()
        return redirect(url_for('cashier.change_password'))
    if request.method == "GET":
        return render_template('cashier/cashier.html', mod=module)


@cashier.route("/logout", methods=["POST"])
def logout():
    cashier_id = request.form["cashier"]
    cashier = Cashier.read_one(Cashier, cashier_id)
    current_session = Session.get_current_session(Session, cashier)
    if current_session:
        current_session.update(0)
    else:
        logout_user()
        flash("Login to start a new session", "info")
    return redirect(url_for('user.login'))