from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from glamsage.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    from glamsage.app.admin.views import admins
    from glamsage.app.errors.handlers import errors
    from glamsage.app.glamsage.views import glamsage
    from glamsage.app.payments.views import payments
    from glamsage.app.posts.views import posts
    from glamsage.app.providers.views import providers
    from glamsage.app.services.views import services

    app.register_blueprint(services)
    app.register_blueprint(admins)
    app.register_blueprint(errors)
    app.register_blueprint(glamsage)
    app.register_blueprint(payments)
    app.register_blueprint(posts)
    app.register_blueprint(providers, url_prefix="/sellers")

    # temporary import as most of the table  are already not located in the app folder
    from glamsage.app.admin.models import Admin
    from glamsage.app.payments.models import BkashPayment, Payment
    from glamsage.app.posts.models import Post
    from glamsage.app.providers.models import Provider
    from glamsage.app.services.models import Service
    from glamsage.models.complain import Flag, Report
    from glamsage.models.notification import Notification
    from glamsage.models.sale import TotalSale

    return app
