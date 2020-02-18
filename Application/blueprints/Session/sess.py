from flask import Blueprint, render_template, url_for, request, redirect, flash
from Application.database.model import Session, User, Cashier, session
import datetime
from Application.blueprints import utils
from flask_login import current_user, login_required


sess = Blueprint('session', __name__, url_prefix="/session")

module = sess.name


@sess.route("/session", methods=["GET", "POST"])
@login_required
def get_sessions():
    if request.method == "GET":
        sessions = Session.read(Session)
        session_page = Session.read_limit(Session, 1, 10)
        cashiers = Cashier.read(Cashier)
        return render_template('manager/cashier-session.html', sessions=sessions, session_page=session_page, mod=module, cashiers=cashiers)
    elif request.method == "POST":
        return redirect(url_for('session.get_sessions'))


@sess.route("/session_page", methods=["GET"])
@login_required
def get_session_page():
    page = request.args.get("page")
    if page:
        page = int(page)
        if page == 0:
            return redirect(url_for('session.get_sessions'))
        session_page = Session.read_limit(Session, page, 10)
        sessions = session_page.items
        cashiers = Cashier.read(Cashier)
        return render_template("manager/cashier-session.html", mod=module, sessions=sessions, session_page=session_page, current_page=page, cashiers=cashiers)
    else:
        return redirect(url_for("order.get_sessions"))


@sess.route("/close", methods=["GET", "POST"])
@login_required
def close_session():
    if request.method == "GET":
        return render_template('cashier/close-session.html', mod=module )
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cash = request.form["cash"]
        user = User.find_user(User, username, password)
        if user and user.cashier == current_user.cashier:
            current_session = Session.get_current_session(Session, current_user.cashier)
            if current_session:
                current_session.update(cash)
                return redirect(url_for('user.logout'))
            else:
                flash("Looks like you do not have a session running", "info")
                return redirect(url_for('session.close_session'))
        else:
            flash("Unknown User", "danger")
            return redirect(url_for('session.close_session'))


@sess.route("/filter", methods=["GET"])
@login_required
def filter_sessions():
    if request.method == "GET":
        cashiers = Cashier.read(Cashier)

        cashier = request.args["cashier"]
        _from = request.args["from"]
        to = request.args["to"]

        if _from:
            _from = utils.convert_date_from_html(_from)
        else:
            _from = datetime.datetime(2000, 1, 1)
        if to:
            to = utils.convert_date_from_html(to)
        else:
            to = datetime.datetime(3000, 1, 1)

        sessions = Session.filter(Session, cashier, _from, to)

        # Avoid error on changing str to int
        if cashier == "":
            cashier = 0

        return render_template("manager/cashier-session.html", mod=module, sessions=sessions,
                               cashiers=cashiers, cashier_id=int(cashier), today=_from, tomorrow=to)


@sess.route("/terminate/<id>", methods=["POST"])
@login_required
def terminate(id):
    if current_user.manager and request.method == "POST":
        cash = request.form["cash"]
        session = Session.read_one(Session, id)
        session.update(cash)
        flash("Session has been terminated successfully", "info")
        return redirect(url_for("session.get_sessions"))



