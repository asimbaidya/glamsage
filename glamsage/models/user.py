from flask import current_app
from itsdangerous import Serializer
from werkzeug.security import check_password_hash

from glamsage import db


class User(db.Model):
    __mapper_args__ = {
        "polymorphic_identity": "user",  ## type
    }

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # common fields for both client, provider and Admin
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)

    # 1 user can have many notifications
    # they get deleted when user is deleted
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @staticmethod
    def is_unique_email(new_email: str):
        return User.query.filter_by(email=new_email).first() is None

    @staticmethod
    def is_unique_username(new_username: str):
        return User.query.filter_by(username=new_username).first() is None

    @staticmethod
    def verify_user(username: str, password: str):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return user, None
        return None, "Invalid username or password"

    def get_reset_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except Exception:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
