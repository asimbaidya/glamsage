from datetime import datetime

from glamsage import db


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post = db.Column(db.Text, nullable=False)
    client = db.Column(db.Integer, db.ForeignKey("user.username"), nullable=False)
