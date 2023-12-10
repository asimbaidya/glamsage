import os
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from glamsage import db  # type: ignore
from glamsage.app.clients.models import Client
from glamsage.app.payments.models import BkashPayment, Payment
from glamsage.app.providers.models import Provider
from glamsage.app.services.models import Order, Service
from glamsage.models.utils import Cart, CurrentUser
from glamsage.utils.file_manager import generate_unique_filename
from glamsage.utils.login_required import client_login_required, provider_login_required
from glamsage.utils.redirect import redirect_if_not_htmx

services = Blueprint("services", __name__)


@services.route("/services", methods=["GET", "POST"])
def all_service():
    all_services = []
    if request.method == "POST":
        username = session.get("username")
        if not username:
            flash("Login First!!", "info")
            return redirect(url_for("client.login"))
        #
        provider = Provider.query.filter_by(username=username).first()

        title = request.form["title"]
        description = request.form["description"]
        price = request.form["price"]
        cover_image = request.files["cover_image"]

        # save the cover image
        # cover_image_path = os.path.join(app.root_path, "static/service", username)
        cover_image_path = "static/service/" + username + "/" + cover_image.filename

        # save the service
        service = Service(
            title=title,
            description=description,
            price=price,
            cover_image=cover_image_path,
            provider=provider,
        )  # type: ignore

        cover_image.save(cover_image_path)
        db.session.add(service)
        db.session.commit()
    elif request.method == "GET":
        query = request.args.get("query")
        if query:
            all_services = Service.query.filter(
                Service.title.like("%" + query + "%")
                | Service.description.like("%" + query + "%")
            ).all()
        else:
            all_services = Service.query.all()
    return render_template("all_service.html", title="Service", services=all_services)


@services.route("/service/new", methods=["GET"])
@provider_login_required
def new_service():
    return render_template("create_service.html", title="New Service")


@services.route("/service/create", methods=["POST"])
@provider_login_required
def create_service():
    service_title = request.form["title"]
    description = request.form["description"]
    price = request.form["price"]
    cover_image = request.files["cover_image"]
    category = request.form["category"]

    provider = Provider.query.filter_by(username=CurrentUser.get_username()).first()
    if not provider:
        flash("Login First!!", "info")
        return redirect(url_for("client.login"))

    # save the cover image
    filename = generate_unique_filename(cover_image.filename)

    target_directory = os.path.join("glamsage", "static", "media", "services")
    os.makedirs(target_directory, exist_ok=True)

    file_path = os.path.join(target_directory, filename)
    cover_image.save(file_path)

    # save the service
    service = Service(
        title=service_title,
        description=description,
        price=price,
        cover_image=filename,
        provider=provider.id,
        category=category,
    )  # type: ignore

    flash("Service created successfully", "success")
    db.session.add(service)
    db.session.commit()
    return render_template("create_service.html", title="New Service")


# serfice route
@services.route("/service/<int:service_id>", methods=["GET", "POST"])
def service(service_id: int):
    service = Service.query.get_or_404(service_id)
    if request.method == "POST":
        username = session.get("username")
        if not username:
            flash("Login First!!", "info")
            return redirect(url_for("client.login"))
        #
        provider = Provider.query.filter_by(username=username).first()

        title = request.form["title"]
        description = request.form["description"]
        price = request.form["price"]
        cover_image = request.files["cover_image"]

        # save the cover image
        # cover_image_path = os.path.join(app.root_path, "static/service", username)
        cover_image_path = "static/service/" + username + "/" + cover_image.filename

        # save the service
        service = Service(
            title=title,
            description=description,
            price=price,
            cover_image=cover_image_path,
            provider=provider,
        )  #  type: ignore
    return render_template("service.html", title=service.title, service=service)


# add to cart
@services.route("/add_to_cart/")
def add_to_cart():
    # get service id from request
    service_id = request.args.get("service_id")
    if not service_id:
        abort(404)

    # add to cart
    msg, flag = Cart.add_to_cart(int(service_id))

    # return response
    response_data = {
        "cart_count": session["cart"]["total_services"],
        "total_price": session["cart"]["total_price"],
        "msg": msg,
        "flag": flag,
    }
    return jsonify(response_data)


# remove from cart
@services.route("/remove_from_cart/")
def remove_from_cart():
    service_id = request.args.get("service_id")
    if not service_id:
        abort(404)

    msg, flag = Cart.remove_from_cart(int(service_id))

    response_data = {
        "cart_count": session["cart"]["total_services"],
        "total_price": session["cart"]["total_price"],
        "msg": msg,
        "flag": flag,
    }

    return jsonify(response_data)


@services.route("/cart")
@client_login_required
def show_cart():
    cart_items_with_providers, prices = Cart.get_cart_details()

    print(cart_items_with_providers)
    print(prices)
    return render_template(
        "cart.html",
        title="Cart",
        total_price=session["cart"]["total_price"],
        total_services=session["cart"]["total_services"],
        prices=prices,
        cart_w_providers=cart_items_with_providers,
    )


@services.route("/clear_cart")
def clear_cart():
    Cart.clear_cart()
    return redirect(url_for("services.all_service"))


# todo
@services.route("/make_order", methods=["post"])
@client_login_required
def make_order():
    if request.method == "POST":
        provider = request.form["provider"]
        app_date = request.form["app_date"]
        app_time = request.form["app_time"]
        price = request.form["price"]
        bkash_trx = request.form["bkash_trx"]
        price = float(price)

        # this clear cart even if the order was unsuccessful in case of bkash
        services = Cart.get_service_by_provider(provider)
        if services is None:
            flash("No service found", "info")
            return redirect(url_for("services.all_service"))

        client = Client.query.filter_by(username=CurrentUser.get_username()).first()
        if not client:
            flash("Login First!!", "info")
            return redirect(url_for("client.login"))

        provider = Provider.query.filter_by(username=provider).first()
        if not provider:
            flash("No provider found", "info")
            return redirect(url_for("services.show_cart"))

        app_datetime_str = f"{app_date} {app_time}"
        due_date = datetime.strptime(app_datetime_str, "%Y-%m-%d %H:%M")

        # now check if trx is valid
        if bkash_trx:
            bkash_payment = BkashPayment.query.filter_by(bkash_trx_id=bkash_trx).first()

            if bkash_payment is None:
                payment = Payment(
                    method="Bkash",
                    amount=price,
                    date=datetime.utcnow(),
                    provider_id=provider.id,
                )  # type: ignore
                db.session.add(payment)
                db.session.commit()
                bkash_payment = BkashPayment(
                    bkash_trx_id=bkash_trx,
                    amount=price,
                    pid=payment.id,
                    payment_id=payment.id,
                )  # type: ignore

                order = Order(
                    client_id=client.id,
                    provider_id=provider.id,
                    status="PrePaid",
                    due_date=due_date,
                    payment_method="Bkash",
                    price=price,
                )  # type: ignore

                db.session.add(bkash_payment)
                db.session.add(order)
                db.session.commit()

                flash(
                    "Your Prepaid Order has been Requested(Client paid First)", "danger"
                )
                return redirect(url_for("services.show_cart"))
            else:
                # not none
                # check if verified
                if bkash_payment.is_verified:
                    flash("bkash_trx is already verified", "error")
                    return redirect(url_for("services.show_cart"))
                elif not bkash_payment.is_verified:
                    # check if amount is equal
                    if bkash_payment.amount == price:
                        payment = Payment.query.filter_by(id=bkash_payment.pid).first()
                        if payment is None:
                            flash(
                                f"No payment exist with {bkash_payment.id},but has this bkash_trx",
                                "error",
                            )
                            return redirect(url_for("services.show_cart"))
                        #  so alreday paid and client just entered trx late, add and make order confirmed
                        # but status is nto confirmed, as confirmed means provider received the money

                        order = Order(
                            client_id=client.id,
                            provider_id=provider.id,
                            status="Pendin(Paid)",
                            # completed_timestamp=datetime.utcnow(), # when manuallly provider clicks
                            due_date=due_date,
                            payment_method="Bkash",
                            price=price,
                        )  # type: ignore

                        # payment is verified
                        payment.is_verified = True
                        bkash_payment.is_verified = True
                        db.session.commit()
                        flash(
                            f"bkash_trx is verified, {bkash_trx} already exist(Provided Added trx First)",
                            "success",
                        )
                        return redirect(url_for("services.show_cart"))

                    else:
                        flash("amount is not equal to the amount_received", "danger")
                        return redirect(url_for("services.show_cart"))

        # (not money issue)
        order = Order(
            client_id=client.id,
            provider_id=provider.id,
            status="Pending",
            due_date=due_date,
            price=price,
        )  # type: ignore

        for service in services:
            order.services.append(service)
        db.session.add(order)
        db.session.commit()
        flash("Order placed successfully", "success")
    return redirect(url_for("services.show_cart"))


@services.route("/service/id/<int:service_id>")
def service_by_id(service_id):
    service = Service.query.get_or_404(service_id)
    reviews = []  # not my part
    ratings = []
    for review in reviews:
        ratings.append(review.rating)
    if len(ratings) == 0:
        avg_rating = "No rating yet"
    else:
        avg_rating = sum(ratings) / len(ratings)
    return render_template(
        "single_service.html", title=service.title, service=service, rating=avg_rating
    )


@services.route("/cancel_order/<int:order_id>")
@client_login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = "Cancelled"
    db.session.commit()
    flash("Order cancelled successfully", "success")
    return redirect(url_for("clients.client", username=CurrentUser.get_username()))


@services.route("/confirm/<int:order_id>")
@provider_login_required
def cash_confirm_order(order_id):
    order = Order.query.get_or_404(order_id)

    payment = Payment(
        method="Cash",
        amount=order.price,
        date=datetime.utcnow(),
        is_successful=True,
        order_id=order.id,
        is_verified=True,
    )  # type: ignore

    order.status = "Confirmed"
    order.completed_timestamp = datetime.utcnow()
    order.payment_id = payment.id
    order.payment_method = payment.method

    db.session.add(payment)
    db.session.commit()
    flash("Order Confirmed", "success")
    return redirect(url_for("providers.dashboard", username=CurrentUser.get_username()))


@services.route("/confirm/b/<int:order_id>")
@provider_login_required
def bcash_confirm_order(order_id):
    order = Order.query.get_or_404(order_id)

    payment = Payment.query.filter_by(order_id=order.id).first()
    if not payment:
        flash("No payment exist", "danger")
        return redirect(
            url_for("providers.dashboard", username=CurrentUser.get_username())
        )

    if payment.is_verified:
        order.status = "Confirmed"
        flash("Confirmed", "danger")
        return redirect(
            url_for("providers.dashboard", username=CurrentUser.get_username())
        )
    else:
        flash("Payment is not verified, Enter trx first", "danger")
        return redirect(
            url_for("providers.dashboard", username=CurrentUser.get_username())
        )
