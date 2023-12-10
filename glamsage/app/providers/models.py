from datetime import time

from glamsage import db
from glamsage.models.user import User


class Provider(User):
    # __mapper_args__ = {
    #     "polymorphic_identity": "provider",
    # }
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)  # trigger
    brand_title = db.Column(db.String(20), unique=True, nullable=False)

    opening_time = db.Column(db.Time, nullable=True, default=time(10, 0, 0))
    closing_time = db.Column(db.Time, nullable=True, default=time(22, 0, 0))
    weekdays = db.Column(db.String(20), nullable=True, default="Friday")

    facebook_url = db.Column(db.String(255), nullable=True)
    instagram_url = db.Column(db.String(255), nullable=True)
    website_url = db.Column(db.String(255), nullable=True)

    profile_image = db.Column(
        db.String(60), nullable=True, default="default-brand-profile.jpg"
    )
    cover_image = db.Column(
        db.String(60), nullable=True, default="default-brand-cover.jpg"
    )

    def __repr__(self):
        return f"Provider('{self.brand_title}', '{self.email}', '{self.username}')"

    @staticmethod
    def verify_login(username: str, password: str):
        user, error = Provider.verify_user(username, password)
        if error or not user:
            return None, error
        provider = Provider.query.filter_by(id=user.id).first()
        if not provider:
            return None, "Provider not found"
        return provider, None
