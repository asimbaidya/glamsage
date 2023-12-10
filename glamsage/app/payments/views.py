from datetime import datetime

from flask import Blueprint, abort, flash, redirect, request, url_for

from glamsage import db
from glamsage.app.payments.models import BkashPayment, Payment
from glamsage.app.services.models import Order
from glamsage.models.utils import CurrentUser
from glamsage.utils.login_required import client_login_required, provider_login_required

payments = Blueprint("payments", __name__)


@payments.route("/add_bkash_trx/<string:username>", methods=["POST"])
@provider_login_required
def add_bkash_trx(username: str):
    bkash_trx = request.form.get("bkash_trx")
    amount = request.form.get("amount")

    if not bkash_trx or not amount:
        flash("bkash_trx/amount is empty", "danger")
        return redirect(url_for("providers.dashboard", username=username))

    # important(price are float in db)
    amount = float(amount)

    bkash_payment = BkashPayment.query.filter_by(bkash_trx_id=bkash_trx).first()

    if bkash_payment is None:
        # so create a new payment
        new_payment = Payment(
            method="Bkash",
            amount=amount,
            date=datetime.utcnow(),
            provider_id=CurrentUser.get_id(),
        )  # type: ignore
        db.session.add(new_payment)
        db.session.commit()

        new_bkash_payment = BkashPayment(
            bkash_trx_id=bkash_trx,
            amount=new_payment.amount,
            pid=new_payment.id,
        )  # type: ignore

        db.session.add(new_bkash_payment)
        db.session.commit()

        flash("New bkash_trx is added(Provider Added First)", "success")
        return redirect(url_for("providers.dashboard", username=username))

    else:
        print(bkash_payment)
        print(bkash_payment.is_verified)
        print(bkash_payment.amount)
        print(amount)
        print(bkash_payment.amount == amount)
        print(bkash_payment.amount == float(amount))
        print("🔴", bkash_payment.payment_id)

        # already exist
        if bkash_payment.is_verified:
            flash("Invalid trx id, bkash_trx is already verified", "error")
            return redirect(url_for("providers.dashboard", username=username))
        else:
            if amount == bkash_payment.amount:
                payment = Payment.query.filter_by(id=bkash_payment.pid).first()
                if payment is None:
                    flash(
                        f"No payment exist with {bkash_payment.id},but has this bkash_trx",
                        "error",
                    )
                    return redirect(url_for("providers.dashboard", username=username))

                order = Order.query.filter_by(id=payment.order_id).first()
                if order is None:
                    flash(
                        f"No order exist with {payment.order_id},but has this bkash_trx",
                        "error",
                    )
                    return redirect(url_for("providers.dashboard", username=username))

                order.status = "Confirmed"
                order.payment_method = "Bkash"

                payment.is_verified = True
                bkash_payment.is_verified = True
                db.session.commit()
                flash(
                    f"bkash_trx is verified, {bkash_trx} already exist(Client Added First)",
                    "success",
                )
                return redirect(url_for("providers.dashboard", username=username))

            else:
                flash("Paid ammount didn't matched", "danger")
                return redirect(url_for("providers.dashboard", username=username))
