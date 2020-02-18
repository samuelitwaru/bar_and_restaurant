from flask import Blueprint, render_template, request, redirect, url_for
from Application.database.model import Waiter, session
from flask_login import login_required

waiter = Blueprint('waiter', __name__, url_prefix="/waiter")

module = waiter.name


@waiter.route("/")
@login_required
def get_waiters():
    waiters = Waiter.read(Waiter)
    return render_template("manager/waiters.html", mod=module, waiters=waiters)


@waiter.route("/add", methods=["POST"])
@login_required
def add_waiter():
    if request.method == "POST":
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        waiter = Waiter(first_name, last_name)
        session.close()
        
    return redirect(url_for('waiter.get_waiters'))


@waiter.route("/edt", methods=["POST", "GET"])
@login_required
def edit_waiter():
    if request.method == "POST":
        waiter_id = request.form["waiter"]
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        waiter = Waiter.read_one(Waiter, waiter_id)
        waiter.update(first_name, last_name)
        session.close()
        return redirect(url_for('waiter.get_waiters'))

    elif request.method == "GET":
        waiter_id = request.args["waiter"]
        waiter = Waiter.read_one(Waiter, waiter_id)
        return render_template("manager/waiters.html", mod=module, waiter_to_edit=waiter)


@waiter.route("/delete", methods=["POST"])
@login_required
def delete_waiter():
    if request.method == "POST":
        waiter_id = request.form["waiter"]
        waiter = Waiter.read_one(Waiter, waiter_id)
        Waiter.delete(waiter)
        return redirect(url_for('waiter.get_waiters'))






























