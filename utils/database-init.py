import os
import random
import sys
from datetime import datetime

# (3) line to ensure glamsage is child dir of current path
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

if __name__ == "__main__":
    from werkzeug.security import generate_password_hash

    from app import app
    from glamsage import db
    from glamsage.app.admin.models import Admin
    from glamsage.app.clients.models import Client
    from glamsage.app.payments.models import BkashPayment, Payment
    from glamsage.app.posts.models import Post
    from glamsage.app.providers.models import Provider
    from glamsage.app.reviews.models import Rating, Reply, Review, ReviewLike
    from glamsage.app.services.models import Service
    from glamsage.models.complain import Report
    from glamsage.models.notification import Notification
    from glamsage.models.sale import TotalSale

    app.app_context().push()
    db.create_all()

    print(f"{Admin.__tablename__} table created")  # type: ignore
    print(f"{Client.__tablename__} table created")  # type: ignore
    print(f"{Provider.__tablename__} table created")  # type: ignore
    print(f"{Service.__tablename__} table created")  # type: ignore
    print(f"{Post.__tablename__} table created")  # type: ignore
    print(f"{Payment.__tablename__} table created")  # type: ignore
    print(f"{BkashPayment.__tablename__} table created")  # type: ignore
    print(f"{Review.__tablename__} table created")  # type: ignore
    print(f"{ReviewLike.__tablename__} table created")  # type: ignore
    print(f"{Reply.__tablename__} table created")  # type: ignore
    print(f"{Rating.__tablename__} table created")  # type: ignore
    print(f"{Report.__tablename__} table created")  # type: ignore
    print(f"{Notification.__tablename__} table created")  # type: ignore
    print(f"{TotalSale.__tablename__} table created")  # type: ignore

    dummy_admins = [
        {
            "username": "admin1",
            "email": "admin1@example.com",
            "password": "password1",
            "phone": "123-456-7890",
        },
        {
            "username": "admin2",
            "email": "admin2@example.com",
            "password": "password2",
            "phone": "987-654-3210",
        },
    ]

    for admin_data in dummy_admins:
        admin_data["password"] = generate_password_hash(admin_data["password"])
        admin = Admin(**admin_data)
        db.session.add(admin)

    # List of dummy clients
    dummy_clients = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "username": "john_doe",
            "email": "john@example.com",
            "password": "password1",
            "location": "City1",
            "phone": "123-456-7890",
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "jane_doe",
            "email": "jane@example.com",
            "password": "password2",
            "location": "City2",
            "phone": "987-654-3210",
        },
        {
            "first_name": "Alice",
            "last_name": "Johnson",
            "username": "alice_j",
            "email": "alice@example.com",
            "password": "password3",
            "location": "City3",
            "phone": "111-222-3333",
        },
        {
            "first_name": "Bob",
            "last_name": "Smith",
            "username": "bob_smith",
            "email": "bob@example.com",
            "password": "password4",
            "location": "City4",
            "phone": "444-555-6666",
        },
        {
            "first_name": "Eva",
            "last_name": "Williams",
            "username": "eva_w",
            "email": "eva@example.com",
            "password": "password5",
            "location": "City5",
            "phone": "777-888-9999",
        },
        {
            "first_name": "David",
            "last_name": "Miller",
            "username": "david_m",
            "email": "david@example.com",
            "password": "password6",
            "location": "City6",
            "phone": "123-987-6543",
        },
        {
            "first_name": "Sophia",
            "last_name": "Brown",
            "username": "sophia_b",
            "email": "sophia@example.com",
            "password": "password7",
            "location": "City7",
            "phone": "987-654-3210",
        },
        {
            "first_name": "Ryan",
            "last_name": "Davis",
            "username": "ryan_d",
            "email": "ryan@example.com",
            "password": "password8",
            "location": "City8",
            "phone": "456-789-0123",
        },
        {
            "first_name": "Emma",
            "last_name": "Taylor",
            "username": "emma_t",
            "email": "emma@example.com",
            "password": "password9",
            "location": "City9",
            "phone": "987-123-4567",
        },
        {
            "first_name": "Michael",
            "last_name": "Clark",
            "username": "michael_c",
            "email": "michael@example.com",
            "password": "password10",
            "location": "City10",
            "phone": "567-890-1234",
        },
    ]

    # insert dummy clients into the database
    for client_data in dummy_clients:
        client_data["password"] = generate_password_hash(client_data["password"])
        client = Client(**client_data)
        db.session.add(client)

    ##

    dummy_providers = [
        {
            "brand_title": "Glamour Haven",
            "username": "glam_haven",
            "email": "glam@example.com",
            "password": "password1",
            "phone": "123-456-7890",
            "location": "City1",
            "facebook_url": "https://facebook.com/glamourhaven",
            "instagram_url": "https://instagram.com/glamourhaven",
        },
        {
            "brand_title": "Radiant Styles",
            "username": "radiant_styles",
            "email": "radiant@example.com",
            "password": "password2",
            "phone": "987-654-3210",
            "location": "City2",
            "facebook_url": "https://facebook.com/radiantstyles",
            "instagram_url": "https://instagram.com/radiantstyles",
        },
    ]
    # insert dummy clients into the database
    for provider_data in dummy_providers:
        provider_data["password"] = generate_password_hash(provider_data["password"])
        provider = Provider(**provider_data)
        db.session.add(provider)

    ##
    dummy_services = [
        {
            "title": "Glamorous Hair Affair",
            "description": "Indulge in the ultimate Hair experience with Glam Haven. A glamorous affair of luxury and style awaits you. Your hair, like never before!",
            "price": 500,
            "discount": round(random.uniform(5.0, 20.0), 2),
            "cover_image": "sv-hair.png",
            "provider": "glam_haven",
            "category": "Hair",
        },
        {
            "title": "Radiant Skin Rejuvenation",
            "description": "Indulge in the ultimate Skin experience with Radiant Styles. A rejuvenating blend of luxury and style awaits you. Your skin, like never before!",
            "price": 510,
            "discount": round(random.uniform(5.0, 20.0), 2),
            "cover_image": "sv-glow-skin.png",
            "provider": "radiant_styles",
            "category": "Skin",
        },
        {
            "title": "Elegant Nail Artistry",
            "description": "Indulge in the ultimate Nails experience with Elegance Emporium. An elegant artistry of luxury and style awaits you. Your nails, like never before!",
            "price": 520,
            "discount": round(random.uniform(5.0, 20.0), 2),
            "cover_image": "sv-nail-art.png",
            "provider": "glam_haven",
            "category": "Nails",
        },
        {
            "title": "Chic Charm Makeup Magic",
            "description": "Indulge in the ultimate Makeup experience with Chic Charm. A magical blend of luxury and style awaits you. Your makeup, like never before!",
            "price": 530,
            "discount": round(random.uniform(5.0, 20.0), 2),
            "cover_image": "sv-makeup.png",
            "provider": "glam_haven",
            "category": "Makeup",
        },
        {
            "title": "Divine Spa Retreat",
            "description": "Indulge in the ultimate Spa experience with Divine Tresses. A divine retreat of luxury and style awaits you. Your spa experience, like never before!",
            "price": 540,
            "discount": round(random.uniform(5.0, 20.0), 2),
            "cover_image": "sv-massage.png",
            "provider": "glam_haven",
            "category": "Spa",
        },
        {
            "title": "Glamorous Hair Extravaganza",
            "description": "Indulge in the ultimate Hair experience with Glam Haven. A glamorous extravaganza of luxury and style awaits you. Your hair, like never before!",
            "price": 580,
            "discount": round(random.uniform(5.0, 20.0), 2),
            "cover_image": "hair-hair.png",
            "provider": "glam_haven",
            "category": "Hair",
        },
        {
            "title": "Radiant Skin Bliss",
            "description": "Indulge in the ultimate Skin experience with Radiant Styles. A blissful blend of luxury and style awaits you. Your skin, like never before!",
            "price": 590,
            "discount": round(random.uniform(5.0, 20.0), 2),
            "cover_image": "sv-glow-skin.png",
            "provider": "radiant_styles",
            "category": "Skin",
        },
    ]

    for service_data in dummy_services:
        service = Service(**service_data)
        db.session.add(service)

    # dummey posts
    dummy_posts = [
        {
            "post": "I recently had a makeup session at Glam Sage Beauty Salon, and it was an absolute delight! From the moment I stepped in, the atmosphere was vibrant and professional, instantly making me feel excited about the transformation ahead.",
            "client": "john_doe",
        },
        {
            "post": "The facilities were immaculate, with a calming ambiance that helped me unwind completely. The use of high-quality products and the staff's attention to detail in every aspect of the service really stood out.",
            "client": "jane_doe",
        },
        {
            "post": "I recently had a makeup session at Glam Sage Beauty Salon, and it was an absolute delight! From the moment I stepped in, the atmosphere was vibrant and professional, instantly making me feel excited about the transformation ahead.",
            "client": "alice_j",
        },
        {
            "post": "The makeup artist was a true artist, blending skill with creativity. She listened to my preferences, provided valuable suggestions, and worked her magic. The result was a flawless, stunning look that perfectly complemented my features and the occasion.",
            "client": "bob_smith",
        },
        {
            "post": "This is a sample post for eva_w",
            "client": "eva_w",
        },
        {
            "post": "This is a sample post for david_m",
            "client": "david_m",
        },
        {
            "post": "This is a sample post for sophia_b",
            "client": "sophia_b",
        },
        {
            "post": "This is a sample post for ryan_d",
            "client": "ryan_d",
        },
        {
            "post": "This is a sample post for emma_t",
            "client": "emma_t",
        },
        {
            "post": "This is a sample post for michael_c",
            "client": "michael_c",
        },
    ]
    for post_data in dummy_posts:
        post = Post(**post_data)
        db.session.add(post)

    # Commit the changes to the database
    db.session.commit()
