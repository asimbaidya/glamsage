from flask import Blueprint, flash, redirect, render_template, request, url_for

from glamsage import db
from glamsage.app.clients.models import Client
from glamsage.app.posts.models import Post
from glamsage.models.utils import CurrentUser
from glamsage.utils.login_required import client_login_required

posts = Blueprint("posts", __name__)


# create  post
@posts.route("/post/new", methods=["GET", "POST"])
@client_login_required
def new_post():
    return render_template("create_post.html", title="New Post")


@posts.route("/post/create", methods=["POST"])
@client_login_required
def create_post():
    print("🔴🔴🔴")
    post = request.form.get("post")
    client = Client.query.filter_by(username=CurrentUser.get_username()).first()

    new_post = Post(post=post, client=client.username)  # type: ignore
    db.session.add(new_post)
    db.session.commit()

    flash("Post created successfully", "success")
    return redirect(url_for("glamsage.home"))
