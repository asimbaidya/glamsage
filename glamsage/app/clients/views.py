import os
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash

from glamsage import db, mail
from glamsage.app.clients.models import Client
from glamsage.app.providers.models import Provider
from glamsage.app.services.models import Order, Service
from glamsage.models.utils import Cart, CurrentUser
from glamsage.utils.file_manager import generate_unique_filename
from glamsage.utils.login_required import client_login_required

clients = Blueprint("clients", __name__)


# todo
@clients.route("/client/<string:username>", methods=["GET", "POST"])
@client_login_required
def client(username: str):
    if CurrentUser.get_username() != username:
        flash("You are not authorized to view this page!", "danger")
        return redirect(url_for("glamsage.home"))

    user = Client.query.filter_by(username=username).first()
    if not user:
        abort(404)
    orders = Order.query.filter_by(client_id=user.id).all()
    profile_image = url_for("static", filename=f"media/clients/{user.profile_image}")

    # using order object as a dict
    order_len = len(orders)
    for order in orders:
        provider_id = order.provider_id
        provider = Provider.query.filter_by(id=provider_id).first()
        if not provider:
            abort(404)
        provider_profile = url_for(
            "static", filename=f"media/providers/{provider.profile_image}"
        )  # type: ignore
        order.provider_profile = provider_profile
        order.provider_name = provider.brand_title
        order.total_services = Order.query.filter_by(
            provider_id=provider_id, client_id=user.id
        ).count()

    return render_template(
        "clients/client.html",
        title=f"@{user.username}",
        user=user,
        profile_image=profile_image,
        order_len=order_len,
        orders=orders,
    )

    # if request.method == "POST":
    #     username = request.form["username"]
    #     email = request.form["email"]

    #     user = Client.query.filter_by(username=session["username"]).first()

    #     # check if username or email already exists
    #     if (
    #         user.username != username
    #         and db.session.query(Client).filter(Client.username == username).first()
    #         != None
    #     ):
    #         flash("Clientname already exists", "info")
    #         return redirect(url_for("clients.register"))
    #     if (
    #         user.email != email
    #         and db.session.query(Client).filter(Client.email == email).first() != None
    #     ):
    #         flash("Email already exists", "info")
    #         return redirect(url_for("clients.register"))

    #     user.username = username
    #     user.email = email
    #     db.session.commit()
    #     session["username"] = user.username

    # user = Client.query.filter_by(username=session["username"]).first()
    # profile_image = url_for("static", filename=f"media/clients/{user.profile_image}")

    # orders = Order.query.filter_by(client_id=user.id).all()
    # return render_template(
    #     "clients/client.html",
    #     title=f"@{user.username}",
    #     user=user,
    #     profile_image=profile_image,
    #     orders=orders,
    # )


@clients.route("/updateclient/<string:username>", methods=["POST"])
@client_login_required
def updateclient(username: str):
    if CurrentUser.get_username() != username:
        flash("You are not authorized to view this page!", "danger")
        return redirect(url_for("glamsage.home"))

    profile_image = request.files["profile_image"]
    # need to save in static/user-profiles/<username>.jpg
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    phone = request.form["phone"]
    location = request.form["location"]

    client = Client.query.filter_by(username=username).first()
    if not client:
        abort(404)

    if first_name:
        client.first_name = first_name

    if last_name:
        client.last_name = last_name

    if phone:
        client.phone = phone

    if location:
        client.location = location

    if profile_image and profile_image.filename:
        filename = generate_unique_filename(profile_image.filename)

        target_directory = os.path.join("glamsage", "static", "media", "clients")
        os.makedirs(target_directory, exist_ok=True)

        file_path = os.path.join(target_directory, filename)
        profile_image.save(file_path)

        #
        client.profile_image = filename
        prifile_path = url_for("static", filename=f"media/clients/{filename}")
        CurrentUser.update_profile_image(prifile_path)

    db.session.commit()
    return redirect(url_for("clients.client", username=username))


# __done__
@clients.route("/register", methods=["GET", "POST"])
def register():
    if CurrentUser.is_authenticated():
        flash("You are alread logged!", "danger")
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(
            password
        )  # Hash the password before storing

        # check if username or email already exists
        if db.session.query(Client).filter(Client.username == username).first() is None:
            flash("Clientname already exists", "info")
            return redirect(url_for("clients.register"))
        if db.session.query(Client).filter(Client.email == email).first() is None:
            flash("Email already exists", "info")
            return redirect(url_for("clients.register"))

        new_user = Client(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_password,
        )  # type: ignore

        db.session.add(new_user)
        db.session.commit()  # Commit changes to the database

        flash("Account created successfully", "info")
        return redirect(url_for("clients.login"))
    return render_template("clients/register.html")


# __done__
@clients.route("/login", methods=["GET", "POST"])
def login():
    if CurrentUser.is_authenticated():
        flash("You are alread logged!", "danger")
        # todo: redirect to client profile
        return redirect(url_for("glamsage.home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        client, error = Client.verify_login(username, password)
        print(client, error)
        if error or not client:
            flash(f"Error {str(error)}", "info")
            return redirect(url_for("clients.login"))

        profile_image = url_for(
            "static", filename=f"media/clients/{client.profile_image}"
        )
        CurrentUser.login(
            profile_image=profile_image, id=client.id, username=username, is_client=True
        )
        # init cart(just pushes cart to session)
        Cart.init_cart()
        flash("Logged in successfully", "success")
        return render_template("layout.html")

    return render_template("clients/login.html")


# __done__
def send_reset_email(user, is_provider=False):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="noreply@app.com", recipients=[user.email]
    )

    if is_provider is True:
        url = url_for("providers.reset_token", token=token, _external=True)
    else:
        url = url_for("clients.reset_token", token=token, _external=True)

    msg.body = f"""To reset your password, visit the following link:
{url}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


# __done__
@clients.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if session.get("logged_in"):
        flash("Please, logout in order to reset password", "info")
        return redirect(url_for("glamsage.home"))
    if request.method == "POST":
        email = request.form["email"]
        if db.session.query(Client).filter(Client.email == email).first() is None:
            flash(f"No user exist with f{email}")
            return redirect(url_for("clients.register"))

        # checking done, now generate a mew token
        user = Client.query.filter_by(email=email).first()
        send_reset_email(user)
        flash("Check your email for reset link!", "info")
        # also redirect to the same page
    return render_template("reset_request.html", title="Reset Password")


# __done__
@clients.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if session.get("logged_in"):
        flash("What the Hell!!", "info")
        return redirect(url_for("glamsage.home"))

    print("token:", token)
    user = Client.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("clients.reset_request"))

    if request.method == "POST":
        password = request.form["password"]

        hashed_password = generate_password_hash(
            password
        )  # Hash the password before storing

        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("clients.login"))
    return render_template("reset_token.html", title="Reset Password")
