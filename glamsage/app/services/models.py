from datetime import datetime

from glamsage import db  # type: ignore
from glamsage.app.payments.models import Payment

# define an association table to represent the many-to-many relationship
order_services_association = db.Table(
    "order_services",
    db.Column("order_id", db.Integer, db.ForeignKey("order.id")),
    db.Column("service_id", db.Integer, db.ForeignKey("service.id")),
)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=True)
    cover_image = db.Column(db.String(60), nullable=True, default="default.jpg")
    provider = db.Column(db.Integer, db.ForeignKey("provider.id"), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    average_rating = db.Column(db.Float, default=0.0)

    # define a relationship to the order model
    orders = db.relationship(
        "Order", secondary=order_services_association, back_populates="services"
    )


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    completed_timestamp = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey("payment.id"), nullable=True)
    payment_method = db.Column(
        db.String(50), db.ForeignKey("payment.method"), nullable=True, default="Cash"
    )

    # define a relationship to the service model
    services = db.relationship(
        "Service", secondary=order_services_association, back_populates="orders"
    )
