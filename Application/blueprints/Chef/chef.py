from flask import Blueprint, render_template, request, redirect, url_for, flash
from Application.database.model import Chef, User, session
from flask_login import login_required, current_user

chef = Blueprint('chef', __name__, url_prefix="/chef")

module = chef.name


@chef.route("/")
@login_required
def get_chefs():
    chefs = Chef.read(Chef)
    return render_template("manager/chefs.html", mod=module, chefs=chefs)


@chef.route("/add", methods=["POST"])
@login_required
def add_chef():
    if request.method == "POST":
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        admin = request.form.get("admin")
        username = request.form["username"]
        password = request.form["password"]
        password1 = request.form["password-1"]
        if admin: admin = True
        else: admin = False

        if password != password1:
            flash('Passwords do not match!')
            return redirect(url_for('chef.get_chefs'))
        user = User(username, password)
        Chef(first_name, last_name, admin, user)
        session.close()
        
    return redirect(url_for('chef.get_chefs'))


@chef.route("/edt", methods=["POST", "GET"])
@login_required
def edit_chef():
    if request.method == "POST":
        chef_id = request.form["chef"]
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        admin = request.form.get("admin")
        username = request.form["username"]
        if admin: admin = True
        else: admin = False
        chef = Chef.read_one(Chef, chef_id)
        chef.update(first_name, last_name, admin, username)
        session.close()
        return redirect(url_for('chef.get_chefs'))

    elif request.method == "GET":
        chef_id = request.args["chef"]
        chef = Chef.read_one(Chef, chef_id)
        return render_template("manager/chefs.html", mod=module, chef_to_edit=chef)


@chef.route("/reset", methods=["POST"])
@login_required
def reset_password():
    if request.method == "POST":
        chef_id = request.form["chef"]
        password = request.form["password"]
        password1 = request.form["password-1"]

        if password != password1:
            flash('Passwords do not match!')
            chef = Chef.read_one(Chef, chef_id)
            return render_template("manager/chefs.html", mod=module, chef_to_edit=chef)

        chef = Chef.read_one(Chef, chef_id)
        chef.update_password(password)
        session.close()
        return redirect(url_for('chef.get_chefs'))


@chef.route("/delete", methods=["POST"])
@login_required
def delete_chef():
    if request.method == "POST":
        chef_id = request.form["chef"]
        chef = Chef.read_one(Chef, chef_id)
        Chef.delete(chef)
        return redirect(url_for('chef.get_chefs'))


@chef.route("/change-password", methods=["POST", "GET"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form["c-password"]
        new_password = request.form["n-password"]
        confirm_password = request.form["r-password"]

        user = User.find_user(User, current_user.username, current_password)
        if user:
            if new_password == confirm_password:
                user.chef.update_password(new_password)
                flash("Passsword resset successfully", "success")
            else:
               flash("Passwords do not match", "danger")
        else:
            flash("Incorrect current password", "danger")
        session.close()
        return redirect(url_for('chef.change_password'))
    if request.method == "GET":
        return render_template('chef/chef.html')
