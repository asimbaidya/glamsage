import os
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    flash,
    make_response,
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
from glamsage.app.payments.models import Payment
from glamsage.app.providers.models import Provider
from glamsage.app.services.models import Order
from glamsage.models.utils import CurrentUser
from glamsage.utils.file_manager import generate_unique_filename
from glamsage.utils.login_required import provider_login_required
from glamsage.utils.redirect import redirect_if_not_htmx

providers = Blueprint("providers", __name__, template_folder="templates")


# provider route
@providers.route("/provider/<string:username>", methods=["GET", "POST"])
@provider_login_required
def provider(username: str):
    if CurrentUser.get_username() != username:
        flash("You are not authorized to view this page!", "danger")
        return redirect(url_for("glamsage.home"))
    provider = Provider.query.filter_by(username=username).first()
    if not provider:
        abort(404)

    orders = Order.query.filter_by(provider_id=provider.id).all()
    profile_image = url_for(
        "static", filename=f"media/providers/{provider.profile_image}"
    )
    cover_image = url_for("static", filename=f"media/providers/{provider.cover_image}")
    print(cover_image)
    return render_template(
        "providers/provider.html",
        title=f"@{provider.username}",
        provider=provider,
        profile_image=profile_image,
        cover_image=cover_image,
        orders=orders,
    )


@providers.route("/updateprovider/<string:username>", methods=["POST"])
@provider_login_required
def updateprovider(username: str):
    if CurrentUser.get_username() != username:
        flash("You are not authorized to view this page!", "danger")
        return redirect(url_for("glamsage.home"))

    facebook_url = request.form["facebook_url"]
    instagram_url = request.form["instagram_url"]
    website_url = request.form["website_url"]
    profile_image = request.files["profile_image"]
    cover_image = request.files["cover_image"]

    provider = Provider.query.filter_by(username=username).first()
    if not provider:
        abort(404)

    if facebook_url:
        provider.facebook_url = facebook_url

    if instagram_url:
        provider.instagram_url = instagram_url

    if website_url:
        provider.website_url = website_url

    files = {"profile_image": profile_image, "cover_image": cover_image}

    for file_type, file in files.items():
        if file and file.filename:
            filename = generate_unique_filename(file.filename)

            target_directory = os.path.join("glamsage", "static", "media", "providers")
            os.makedirs(target_directory, exist_ok=True)

            file_path = os.path.join(target_directory, filename)
            file.save(file_path)

            if file_type == "cover_image":
                provider.cover_image = filename
            else:
                provider.profile_image = filename

            if file_type == "profile_image":
                # Get the URL for the saved file
                file_url = url_for("static", filename=f"media/providers/{filename}")
                # Update the database with the file URL
                CurrentUser.update_profile_image(file_url)

    # Commit changes to the database
    db.session.commit()

    return redirect(url_for("providers.provider", username=username))


@providers.route("/dashboard/<string:username>", methods=["GET", "POST"])
@provider_login_required
def dashboard(username):
    if CurrentUser.get_username() != username:
        flash("You are not authorized to view this page!", "danger")
        return redirect(url_for("glamsage.home"))

    user = Provider.query.filter_by(username=username).first()
    if not user:
        abort(404)
    orders = Order.query.filter_by(provider_id=user.id).all()

    # using order object as a dict
    order_len = len(orders)
    for order in orders:
        client_id = order.client_id
        client = Client.query.filter_by(id=client_id).first()

        if not client:
            abort(404)
        profile_image = url_for(
            "static", filename=f"media/clients/{client.profile_image}"
        )

        order.client_profile = profile_image
        order.client_name = client.username
        order.total_services = len(order.services)

    payments = Payment.query.filter_by(provider_id=user.id).all()
    total_payments = len(payments)
    print(total_payments)

    return render_template(
        "providers/dashboard.html",
        title=f"@{user.username}",
        user=user,
        order_len=order_len,
        orders=orders,
        payments=payments,
        total_payments=total_payments,
    )

    return render_template("providers/dashboard.html", title="Provider Dashboard")

    # if not session.get("logged_in"):
    #     flash("Login First!!", "info")
    #     return redirect(url_for("providers.login"))

    # provider = Provider.query.filter_by(username=session["username"]).first()

    # if not provider:
    #     flash("No provider found", "info")
    #     return redirect(url_for("providers.login"))

    # brand_profile_image = url_for(
    #     "static", filename=f"provider-profiles/{provider.brand_profile_image}"
    # )
    # brand_cover_image = url_for(
    #     "static", filename=f"provider-profiles/{provider.brand_cover_image}"
    # )

    # # orders

    # orders = Order.query.filter_by(client_id=provider.id).all()
    # return render_template(
    #     "providers/dashboard.html",
    #     title=f"@{provider.username}",
    #     provider=provider,
    #     brand_profile_image=brand_profile_image,
    #     brand_cover_image=brand_cover_image,
    #     orders=orders,
    # )


# provider login
@providers.route("/login", methods=["GET", "POST"])
def login():
    if CurrentUser.is_authenticated():
        flash("You are alread logged!", "danger")
        return redirect(url_for("glamsage.home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        provider, error = Provider.verify_login(username, password)

        if error or not provider:
            flash(str(error), "error")
            return redirect(url_for("providers.login"))

        profile_image = url_for(
            "static", filename=f"media/providers/{provider.profile_image}"
        )

        CurrentUser.login(
            profile_image=profile_image,
            id=provider.id,
            username=username,
            is_provider=True,
        )
        flash("Logged in successfully", "success")
        # refresh page, so custom nav for user is loaded
        response = make_response(render_template("layout.html"))
        response.headers["HX-Refresh"] = "true"
        return response

    return render_template("providers/provider_login.html", title="Provider Login")


# provider register
@providers.route("/register", methods=["GET", "POST"])
def register():
    if CurrentUser.is_authenticated():
        flash("You are alread logged!", "danger")

    if request.method == "POST":
        username = request.form["username"]
        brand_title = request.form["brand_title"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        if (
            db.session.query(Provider).filter(Provider.username == username).first()
            is None
        ):
            flash("A provider with this username already Exist", "info")
            return redirect(url_for("providers.register"))

        if db.session.query(Provider).filter(Provider.email == email).first() is None:
            flash("A provider with this email already Exist", "info")
            return redirect(url_for("providers.register"))

        new_provider = Provider(
            brand_title=brand_title,
            username=username,
            email=email,
            password=hashed_password,
        )  # type: ignore

        db.session.add(new_provider)
        db.session.commit()

        flash("New provider added", "info")
        return redirect(url_for("providers.login"))
    return render_template("providers/provider_register.html")


#


# new shits
def send_reset_email(user, is_provider=False):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="noreply@app.com", recipients=[user.email]
    )

    if is_provider == True:
        url = url_for("providers.reset_token", token=token, _external=True)
    else:
        url = url_for("clients.reset_token", token=token, _external=True)

    msg.body = f"""To reset your password, visit the following link:
{url}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


# provider
@providers.route("/provider_reset_password", methods=["GET", "POST"])
def reset_request():
    if session.get("logged_in"):
        flash("Please, logout in order to reset password", "info")
        return redirect(url_for("glamsage.home"))
    if request.method == "POST":
        email = request.form["email"]
        if db.session.query(Provider).filter(Provider.email == email).first() == None:
            flash(f"No Provider exist with f{email}")
            return redirect(url_for("providers.register"))

        # checking done, now generate a mew token
        provider = Provider.query.filter_by(email=email).first()
        send_reset_email(provider, is_provider=True)
        flash("Check your email for reset link!", "info")
        # also redirect to the same page
    return render_template("reset_request.html", title="Reset Password")


@providers.route("/provider_reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if session.get("logged_in"):
        flash("What the Hell!!", "info")
        return redirect(url_for("glamsage.home"))

    provider = Provider.verify_reset_token(token)
    if provider is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("providers.reset_request"))

    if request.method == "POST":
        password = request.form["password"]

        hashed_password = generate_password_hash(
            password
        )  # Hash the password before storing

        provider.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("providers.login"))
    return render_template("reset_token.html", title="Reset Password")
