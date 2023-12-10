from glamsage import db
from glamsage.models.user import User


# to manage users and providers
class Admin(User):
    # __mapper_args__ = {
    #     "polymorphic_identity": "admin",
    # }
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)  # trigger
    profile_image = db.Column(
        db.String(60), nullable=True, default="default-admin-profile.jpg"
    )

    def __repr__(self):
        return f"Admin('{self.username}', '{self.email}')"

    @staticmethod
    def verify_login(username: str, password: str):
        user, error = Admin.verify_user(username, password)
        if error or not user:
            return None, error
        admin = Admin.query.filter_by(id=user.id).first()
        if not admin:
            return None, "Admin not found"
        return admin, None
