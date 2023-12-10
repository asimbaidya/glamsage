from datetime import datetime

from glamsage import db


# one to many(1 user can have many notifications)
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # click or mark as read button
    archived = db.Column(db.Boolean, default=False)  # click or mark as archived button

    # backref for notificitions
    user = db.relationship("User", back_populates="notifications")
