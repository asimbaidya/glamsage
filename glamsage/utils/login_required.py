from functools import wraps

from flask import flash, redirect, url_for

from glamsage.models.utils import CurrentUser


def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if CurrentUser.is_admin():
            return func(*args, **kwargs)
        else:
            flash("Access denied. Admin login required, Visit Home instead", "warning")
            print("Access denied. Admin login required.")
            return redirect("/")

    return wrapper


def client_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if CurrentUser.is_client():
            return func(*args, **kwargs)
        else:
            return "Access denied. Client login required."

    return wrapper


def provider_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if CurrentUser.is_provider():
            return func(*args, **kwargs)
        else:
            return "Access denied. Provider login required."

    return wrapper
