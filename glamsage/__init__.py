from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SECRET_KEY"] = "7lRzwJSWW1KQ3bnQWfcnhcNN1acHQH5LJWvwRmGYDYXuK+clKnjv"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)


# this need to go after app is defined
from glamsage import routes
