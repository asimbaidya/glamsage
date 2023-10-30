from flask import redirect, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from glamsage import app, db
from glamsage.models import User


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/account")
def account():
    user = User.query.filter_by(username=session["username"]).first()
    print(dir(user))
    return render_template("account.html", title="Account", user=user)


# Route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(
            password
        )  # Hash the password before storing

        # check if username or email already exists
        if db.session.query(User).filter(User.username == username).first() != None:
            flash("Username already exists", "info")
            return redirect(url_for("register"))
        if db.session.query(User).filter(User.email == email).first() != None:
            flash("Email already exists", "info")
            return redirect(url_for("register"))

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_password,
        )  # type: ignore

        db.session.add(new_user)
        db.session.commit()  # Commit changes to the database

        flash("Account created successfully", "info")
        return redirect(url_for("login"))
    return render_template("register.html")


# Route for user login,completed
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        flash("You are already logged in", "info")
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["logged_in"] = True
            session["username"] = username
            flash("Logged in successfully", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")


# Route for user logout, completed
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))
