from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from glamsage.app.admin.models import Admin
from glamsage.app.clients.models import Client
from glamsage.app.providers.models import Provider
from glamsage.app.services.models import Order
from glamsage.models.complain import Report
from glamsage.models.user import User
from glamsage.models.utils import CurrentUser
from glamsage.utils.login_required import admin_login_required
from glamsage.utils.redirect import redirect_if_not_htmx

admins = Blueprint("admins", __name__)


# done
@admins.route("/admin/<string:username>")
def admin(username: str):
    if username != CurrentUser.get_username() or not CurrentUser.is_admin():
        flash(f"no admin exist with username {username}", "warning")
        return redirect(url_for("glamsage.home"))

    user = Admin.query.filter_by(username=username).first()
    if not user:
        flash(f"no admin exist with username {username}", "warning")
        return redirect(url_for("glamsage.home"))

    profile_image = url_for("static", filename="media/admins/" + user.profile_image)
    return render_template(
        "admin/admin.html", title="Admin", user=user, profile_image=profile_image
    )


# dashboard (todo)
@admins.route("/dashboard/<string:username>", methods=["GET", "POST"])
@admin_login_required
def dashboard(username):
    if not CurrentUser.is_authenticated() or not CurrentUser.is_admin():
        flash("Your do not have permission to visit /dashboard", "warning")
        return redirect(url_for("glamsage.home"))

    admins = Admin.query.all()
    clients = Client.query.all()
    providers = Provider.query.all()
    reports = Report.query.all()

    for client in clients:
        name = client.first_name + " " + client.last_name
        profile_image = url_for(
            "static", filename="media/clients/" + client.profile_image
        )
        total_order = Order.query.filter_by(client_id=client.id).count()

        client.name = name
        client.profile_image = profile_image
        client.total_order = total_order

    for provider in providers:
        name = provider.brand_title
        profile_image = url_for(
            "static", filename="media/providers/" + provider.profile_image
        )
        total_order = Order.query.filter_by(provider_id=provider.id).count()

        provider.name = name
        provider.profile_image = profile_image
        provider.total_order = total_order

    return render_template(
        "admin/dashboard.html",
        title="Admin Dashboard",
        admins=admins,
        clients=clients,
        providers=providers,
        reports=reports,
    )


# done
@admins.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if CurrentUser.is_authenticated():
        flash("You are alread logged!", "danger")
        # todo: redirect to admin profile
        return redirect(url_for("glamsage.home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin, error = Admin.verify_login(username, password)
        if error or not admin:
            flash(str(error), "error")
            return redirect(url_for("admins.admin_login"))
        print(admin, dir(admin))

        profile_image = url_for(
            "static", filename=f"media/admins/{admin.profile_image}"
        )
        CurrentUser.login(
            profile_image=profile_image, id=admin.id, username=username, is_admin=True
        )
        flash("Logged in successfully", "success")

        # refresh page, so custom nav for user is loaded
        response = make_response(render_template("layout.html"))
        response.headers["HX-Refresh"] = "true"
        return response

    return render_template("admin/admin_login.html")
