from glamsage import db
from glamsage.models.user import User


# TODO: what this line does?
class Client(User):
    # __mapper_args__ = {
    #     "polymorphic_identity": "client",
    # }
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)  # trigger

    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    profile_image = db.Column(
        db.String(60), nullable=True, default="default-client-profile.png"
    )

    # replies = db.relationship("Reply", back_populates="client")  # okey
    # reviews = db.relationship("Review", back_populates="client")

    # likes = db.relationship("Like", back_populates="client")

    def __repr__(self):
        return f"Client('{self.username}', '{self.email}')"

    @staticmethod
    def verify_login(username: str, password: str):
        user, error = Client.verify_user(username, password)
        if error or not user:
            return None, error
        admin = Client.query.filter_by(id=user.id).first()
        if not admin:
            return None, "Client not found"
        return admin, None
