from glamsage import db


class TotalSale(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("provider.id"), primary_key=True)
    total_sales = db.Column(db.Float, nullable=False)

    # 1-1 relation
    provider = db.relationship("Provider", backref=db.backref("total_sales", lazy=True))
