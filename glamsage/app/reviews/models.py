# reviews/models.py
from datetime import datetime

from glamsage import db


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))
    client = db.Column(db.Integer, db.ForeignKey("client.id"))
    # only client can rate a service


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    like_count = db.Column(db.Integer, default=0)

    # client can review a service only once
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    username = db.Column(db.String(20), db.ForeignKey("user.username"), nullable=False)
    replies = db.relationship("Reply", back_populates="review")  # okey
    likes = db.relationship("ReviewLike", back_populates="review")  # okey


# review Like
class ReviewLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    liked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("review.id"), nullable=False)

    review = db.relationship("Review", back_populates="likes")  # okey


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # any user can reply to a review
    review_id = db.Column(db.Integer, db.ForeignKey("review.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    username = db.Column(db.String(20), db.ForeignKey("user.username"), nullable=False)

    # relationships 1-n/n-1
    review = db.relationship("Review", back_populates="replies")  # okey
