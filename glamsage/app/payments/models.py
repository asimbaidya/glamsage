from datetime import datetime

from glamsage import db


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(50), nullable=False, default="Cash")
    amount = db.Column(db.Float, nullable=False)  # false might cause problem, cuz
    date = db.Column(db.DateTime, default=datetime.utcnow)
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id"), nullable=True)

    is_successful = db.Column(
        db.Boolean, default=False
    )  # (we added for reason, but not implementing this now)
    is_verified = db.Column(
        db.Boolean, default=False
    )  # when user enter same it will get verified
    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=True,
    )

    bkash_payment = db.relationship(
        "BkashPayment", back_populates="payment", uselist=False
    )


class BkashPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payment.id"))
    pid = db.Column(db.Integer, nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)
    is_verified = db.Column(db.Boolean)
    bkash_trx_id = db.Column(db.String(50), nullable=False, unique=True)

    payment = db.relationship(
        "Payment", foreign_keys=[payment_id], back_populates="bkash_payment"
    )


"""
CLEINT enters bkash_trx first:
it will check if the bkash_trx is already in the database, then it will check if the bkash_trx is verified or not
if the bkash_trx is verified, then it will return a message that the bkash_trx is already verified
if the bkash_trx is not verified, then it will check if the bkash_trx is successful or not
if the bkash_trx is successful, then it will check if the amount_received is equal to the amount
if the amount_received is equal to the amount, then it will update the bkash_trx as verified
if the amount_received is not equal to the amount, then it will return a message that the amount_received is not equal to the amountj
"""
