from dataclasses import dataclass, field

from flask import abort, session

from glamsage import db
from glamsage.app.services.models import Service


@dataclass
class CurrentUser:
    id: int
    username: str
    profile_image: str
    _is_authenticated: bool = False
    _is_admin: bool = False
    _is_client: bool = False
    _is_provider: bool = False
    _got_notification: bool = False
    _got_new_message: bool = False

    # method are only useable inside python code(not in template )
    # because session sterilizes object into dict(maybe)
    # so, from template, one can only access property prefixed with _

    @staticmethod
    def login(
        id, username, profile_image, is_admin=False, is_client=False, is_provider=False
    ):
        session["current_user"] = CurrentUser(
            id,
            username,
            _is_authenticated=True,
            _is_admin=is_admin,
            _is_client=is_client,
            _is_provider=is_provider,
            profile_image=profile_image,
        )
        return f"Logged in {username}"

    @staticmethod
    def is_authenticated():
        current_user = session.get("current_user")
        print(current_user)
        if current_user and current_user["_is_authenticated"]:
            return True
        else:
            return False

    @staticmethod
    def is_admin():
        current_user = session.get("current_user")
        if current_user and current_user["_is_admin"]:
            return True
        else:
            return False

    @staticmethod
    def is_client():
        current_user = session.get("current_user")
        if current_user and current_user["_is_client"]:
            return True
        else:
            return False

    @staticmethod
    def is_provider():
        current_user = session.get("current_user")
        if current_user and current_user["_is_provider"]:
            return True
        else:
            return False

    @staticmethod
    def get_username():
        current_user = session.get("current_user")
        print(current_user)
        if current_user and current_user["_is_authenticated"]:
            print("🍒", current_user)
            return current_user["username"]
        else:
            return "Not logged in"

    @staticmethod
    def get_id():
        current_user = session.get("current_user")
        if current_user and current_user["_is_authenticated"]:
            return current_user["id"]
        else:
            return "Not logged in"

    @staticmethod
    def logout(username: str):
        print("logged out")
        session.clear()
        return f"Logged out {username}"

    @staticmethod
    def update_profile_image(profile_image: str):
        current_user = session.get("current_user")
        if current_user and current_user["_is_authenticated"]:
            current_user["profile_image"] = profile_image
            session["current_user"] = current_user
            return "Profile image updated"
        else:
            return "Not logged in"


@dataclass
class Cart:
    total_services: int = 0
    total_price: int = 0
    added_services: list = field(default_factory=list)

    @staticmethod
    def init_cart():
        session["cart"] = Cart()

    @staticmethod
    def add_to_cart(service_id: int):
        service = db.session.query(Service).filter(Service.id == service_id).first()
        cart = session["cart"]

        if not cart:
            return "Cart not found, Somethign went wrong in server", -1

        if not service:
            return "Service not found", -1

        if service_id in cart["added_services"]:
            return "Service already in cart", -1
        else:
            cart["added_services"].append(service_id)
            cart["total_services"] += 1
            cart["total_price"] += service.price

        session["cart"] = cart
        return "Service added to cart", 0

    @staticmethod
    def remove_from_cart(service_id: int):
        # cart is not a pure dictionary only(not object)
        cart = session.get("cart")
        service = db.session.query(Service).filter(Service.id == service_id).first()

        if not cart or not service:
            return "Cart/service not found, Somethign went wrong in server", -1

        if service_id in cart["added_services"]:
            cart["added_services"].remove(service_id)
            cart["total_services"] -= 1
            cart["total_price"] -= service.price

            # now update the cart in session again
            session["cart"] = cart
            return "Service removed from cart", 0
        return "Service was not in the cart", -1

    @staticmethod
    def clear_cart():
        # cart is not a pure dictionary only(not object)
        cart = session.get("cart")

        if not cart:
            return "Cart not found, Somethign went wrong in server"

        # cleared(not deleted)
        cart["total_services"] = 0
        cart["total_price"] = 0
        cart["added_services"] = []

        # now update the cart in session again
        session["cart"] = cart

    @staticmethod
    def get_cart_details():
        cart = session.get("cart")
        if not cart:
            abort(404)

        cart_items_with_providers = {}
        prices = {}
        for service_id in cart["added_services"]:
            service = db.session.query(Service).filter(Service.id == service_id).first()
            if not service:
                abort(404)

            if service.provider not in cart_items_with_providers:
                cart_items_with_providers[service.provider] = []
                prices[service.provider] = 0

            prices[service.provider] += service.price
            cart_items_with_providers[service.provider].append(service)

        return cart_items_with_providers, prices

    @staticmethod
    def get_service_by_provider(provider_username):
        cart = session.get("cart")
        if not cart:
            abort(404)

        services = []
        for service_id in cart["added_services"]:
            service = db.session.query(Service).filter(Service.id == service_id).first()
            if not service:
                # if service is not in the database now
                # remove from cart and abort
                Cart.remove_from_cart(service_id)
                abort(404)

            if service.provider == provider_username:
                services.append(service)
                Cart.remove_from_cart(service_id)
        return services
