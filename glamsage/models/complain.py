from datetime import datetime

from glamsage import db


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    complain_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    complain_for = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_handled = db.Column(db.Boolean, default=False)
    flag_id = db.Column(db.Integer, db.ForeignKey("flag.id"), nullable=True)


class Flag(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    reports = db.relationship("Report", backref="flag", lazy=True)  # Add this line
