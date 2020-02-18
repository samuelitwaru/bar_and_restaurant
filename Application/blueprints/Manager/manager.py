from flask import Blueprint, render_template, request, redirect, url_for, flash
from Application.database.model import Manager, User, session
from flask_login import login_required, current_user
from Application import mail
from flask_mail import Message
from Application.blueprints.utils import randomString

manager = Blueprint('manager', __name__, url_prefix="/manager")

module = manager.name


@manager.route("/add-manager", methods=["POST"])
def add_manager():
    if request.method == "POST":
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        email = request.form["email"]
        username = request.form["username"]
        boss_email = request.form["boss-email"]

        password = request.form["password"]
        password1 = request.form["password-1"]
        if password != password1:
            flash('Error. Passwords do not match! Please Try again', "warning")
            return redirect(url_for('user.login'))

        user = User(username, password)
        Manager(first_name, last_name, email, boss_email, user)

        flash("Manager was created successfully", "success")
        session.close()
        return redirect(url_for('user.login'))


@manager.route("/manager", methods=["GET", "POST"])
@login_required
def edit_manager():
    if request.method == "POST":
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        email = request.form["email"]
        username = request.form["username"]
        boss_email = request.form["boss-email"]
        manager = Manager.update(current_user.manager, first_name, last_name, email, username, boss_email)
        flash("Manager details upadated successfully", "success")
        session.close()
        return redirect(url_for('manager.edit_manager'))
    if request.method == "GET":
        return render_template('manager/manager.html')


@manager.route("/change-password", methods=["POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form["c-password"]
        new_password = request.form["n-password"]
        confirm_password = request.form["r-password"]

        user = User.find_user(User, current_user.username, current_password)
        if user:
            if new_password == confirm_password:
                user.manager.update_password(new_password)
                flash("Passsword resset successfully", "success")
            else:
               flash("Passwords do not match", "danger") 
        else:
            flash("Incorrect current password", "danger")
        session.close()
        return redirect(url_for('manager.edit_manager'))
    if request.method == "GET":
        return render_template('manager/manager.html')


@manager.route("/reset-password", methods=["POST", "GET"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            manager = Manager.get_by_email(Manager, email)
            if manager:
                # send email
                new_password = randomString()
                msg = Message("Password Reset", sender='samuelitwaru@gmail.com', recipients=[email])
                msg.body = "Hi "+manager.first_name+" "+manager.last_name+",\nYour new password is:  " + new_password + "\nYour username is:  "+manager.user.username
                try:
                    mail.send(msg)
                    flash("Your Password has been changed", "info")
                    flash(
                        "The reset email has been sent to '" + email + "'. Please sign into your email account to get a new password",
                        'success')
                    manager.update_password(new_password)
                except:
                    flash("Failed! Reset email could not be sent. Make sure you're online and try again", "danger")
            else:
                flash("Incorrect Email", 'danger')
        else:
            flash("Invalid Email", 'danger')
        return redirect(url_for('manager.reset_password'))
    elif request.method == "GET":
        return render_template('global/reset-password.html',  mod=module)