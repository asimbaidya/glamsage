from datetime import datetime

from flask import (
    Blueprint,
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
from glamsage.app.reviews.models import Reply, Review, ReviewLike
from glamsage.models.user import User
from glamsage.models.utils import CurrentUser

reviews = Blueprint("reviews", __name__)


# load reviews for a service
@reviews.route("/load_reviews/<int:service_id>", methods=["GET"])
def load_reviews(service_id: int):
    reviews = Review.query.filter_by(service_id=service_id).all()
    can_like = {}
    for i in range(len(reviews)):
        if (
            ReviewLike.query.filter_by(
                review_id=reviews[i].id, client_id=CurrentUser.get_id()
            ).first()
            is None
        ):
            can_like[reviews[i].id] = True
        else:
            can_like[reviews[i].id] = False

    print(reviews)
    print(can_like)
    if reviews:
        return render_template(
            "reviews.html", reviews=reviews, service_id=service_id, can_like=can_like
        )
    else:
        return "<h3>No review for this Service({service_id})</h3>".format(
            service_id=service_id
        )


@reviews.route("/load_reviews_dsc/<int:service_id>", methods=["GET"])
def load_dsc_reviews(service_id: int):
    reviews = Review.query.filter_by(service_id=service_id).all()
    can_like = {}
    for i in range(len(reviews)):
        if (
            ReviewLike.query.filter_by(
                review_id=reviews[i].id, client_id=CurrentUser.get_id()
            ).first()
            is None
        ):
            can_like[reviews[i].id] = True
        else:
            can_like[reviews[i].id] = False

    reviews = sorted(reviews, key=lambda x: x.reviewed_at, reverse=True)
    if reviews:
        return render_template(
            "reviews.html", reviews=reviews, service_id=service_id, can_like=can_like
        )
    else:
        return "<h3>No review for this Service({service_id})</h3>".format(
            service_id=service_id
        )


@reviews.route("/load_reviews_asc/<int:service_id>", methods=["GET"])
def load_asc_reviews(service_id: int):
    reviews = Review.query.filter_by(service_id=service_id).all()
    can_like = {}
    for i in range(len(reviews)):
        if (
            ReviewLike.query.filter_by(
                review_id=reviews[i].id, client_id=CurrentUser.get_id()
            ).first()
            is None
        ):
            can_like[reviews[i].id] = True
        else:
            can_like[reviews[i].id] = False

    reviews = sorted(reviews, key=lambda x: x.reviewed_at)
    if reviews:
        return render_template(
            "reviews.html", reviews=reviews, service_id=service_id, can_like=can_like
        )
    else:
        return "<h3>No review for this Service({service_id})</h3>".format(
            service_id=service_id
        )


@reviews.route("/submit-review/<int:service_id>", methods=["GET", "POST"])
def submit_review(service_id: int):
    if not (CurrentUser.is_authenticated() and CurrentUser.is_client()):
        print("not logged in")
        abort(404)

    # only client can review, to get client from session
    username = session.get("username")
    username = CurrentUser.get_username()
    client = Client.query.filter_by(username=username).first()
    if client is None:
        print("Client Does not exist")
        abort(404)

    # get review data from form
    content = request.form.get("review")
    rating = request.form.get("rating")

    review = Review(
        content=content,
        rating=rating,
        service_id=service_id,
        client_id=client.id,
        username=username,
    )  # type: ignore
    db.session.add(review)
    db.session.commit()
    print("Commmitted")

    return redirect(url_for("services.service_by_id", service_id=service_id))


@reviews.route("/like/<int:service_id>/<int:review_id>", methods=["GET", "POST"])
def like(service_id: int, review_id: int):
    if not (CurrentUser.is_authenticated() and CurrentUser.is_client()):
        print("not logged in")
        abort(404)

    # only client can review, to get client from session
    username = CurrentUser.get_username()
    client = Client.query.filter_by(username=username).first()

    if client is None:
        print("Client Does not exist")
        abort(404)

    review = Review.query.filter_by(id=review_id).first()
    if review is None:
        print("Review Does not exist")
        abort(404)

    if not ReviewLike.query.filter_by(review_id=review.id, client_id=client.id).first():
        like = ReviewLike(client_id=client.id, review_id=review.id)  # type: ignore
        flash("You liked a review", "success")

        db.session.add(like)
        print("Commmitted")
    else:
        # drop the like now
        db.session.delete(
            ReviewLike.query.filter_by(review_id=review.id, client_id=client.id).first()
        )

    db.session.commit()
    flash("Your Unliked a review", "warning")
    return redirect(url_for("services.service_by_id", service_id=service_id))


@reviews.route("/reply/<int:service_id>/<int:review_id>", methods=["POST"])
def reply(service_id: int, review_id: int):
    if not CurrentUser.is_authenticated():
        print("not logged in")
        abort(404)

    # only client can review, to get client from session
    username = CurrentUser.get_username()
    user = User.query.filter_by(username=username).first()

    if user is None:
        print("User Does not exist")
        abort(404)

    review = Review.query.filter_by(id=review_id).first()
    if review is None:
        print("Review Does not exist")
        abort(404)

    # if not ReviewLike.query.filter_by(review_id=review.id, client_id=client.id).first():
    #     like = ReviewLike(client_id=client.id, review_id=review.id)  # type: ignore
    #     flash("You liked a review", "success")

    #     db.session.add(like)
    #     print("Commmitted")
    # else:
    #     # drop the like now
    #     db.session.delete(
    #         ReviewLike.query.filter_by(review_id=review.id, client_id=client.id).first()
    #     )

    print(request.form.get("reply"))
    reply = Reply(
        content=request.form.get("reply"),
        review_id=review.id,
        user_id=user.id,
        username=username,
    )  # type: ignore

    db.session.add(reply)
    db.session.commit()
    flash("Your Reply Posted", "warning")
    return redirect(url_for("services.service_by_id", service_id=service_id))
