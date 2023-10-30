from glamsage import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_image = db.Column(db.String(60), nullable=True, default="default.jpg")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_title = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    brand_profile_image = db.Column(
        db.String(60), nullable=True, default="default-brand-profile.jpg"
    )
    brand_cover_image = db.Column(
        db.String(60), nullable=True, default="default-brand-cover.jpg"
    )


# to manage users and providers
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_image = db.Column(db.String(60), nullable=True, default="default.jpg")
