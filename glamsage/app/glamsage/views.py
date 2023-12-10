from urllib.parse import quote, urlparse

from flask import (
    Blueprint,
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from glamsage import db
from glamsage.app.clients.models import Client
from glamsage.app.posts.models import Post
from glamsage.app.providers.models import Provider
from glamsage.app.services.models import Service
from glamsage.models.utils import CurrentUser
from glamsage.utils.login_required import admin_login_required
from glamsage.utils.redirect import redirect_if_not_htmx

glamsage = Blueprint("glamsage", __name__)


# @glamsage.route("/ninja_redirect/<path:request_from>")
# def ninja_redirect(request_from):
#     print("Next:", request_from)
#     print("Original URL:", request.url)

#     # Parse the URL
#     parsed_url = urlparse(request_from)
#     print(parsed_url)
#     print(parsed_url.geturl())
#     return render_template("layout.html", next=parsed_url.geturl())


@glamsage.route("/", methods=["GET"])
@glamsage.route("/home", methods=["GET"])
def home():
    posts = db.session.query(Post).all()
    for post in posts:
        client = Client.query.filter_by(username=post.client).first()
        if client is None:
            abort(404)
        profile_image = url_for(
            "static", filename="media/clients/" + client.profile_image
        )
        post.profile_image = profile_image  # type: ignore
    return render_template("home/home.html", title="Home", posts=posts)


@glamsage.route("/about")
def about():
    return render_template("home/about.html", title="About")


# single login for user,provider,admin
@glamsage.route("/logout")
def logout():
    if CurrentUser.is_authenticated():
        print(CurrentUser.get_username())
        CurrentUser.logout(CurrentUser.get_username())
        flash("Logged out successfully", "success")
        return redirect(url_for("glamsage.home"))

    session.clear()
    flash("Your are nto Logged IN!", "warning")
    return redirect(url_for("glamsage.home"))
