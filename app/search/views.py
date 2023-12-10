from html import escape

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

from glamsage import db
from glamsage.app.posts.models import Post
from glamsage.app.providers.models import Provider
from glamsage.app.services.models import Service

searches = Blueprint("searches", __name__)


@searches.route("/search", methods=["GET", "POST"])
def search():
    # extract categories from Services
    categories = Service.query.with_entities(Service.category).distinct().all()
    categories = [escape(category[0]) for category in categories]
    categories.append("All")
    categories = sorted(categories)
    return render_template(
        "search.html",
        categories=categories,
        category_option="All",
        category="All",
        sort_order="Ascending",
    )


@searches.route("/search_results", methods=["GET", "POST"])
def search_results():
    search_query = request.args.get("search")
    category = request.args.get("category")
    sort = request.args.get("sort_order", "asc")
    print(category)

    all_services = set()
    services = Service.query.filter(Service.title.contains(search_query)).all()
    all_services.update(services)
    services = Service.query.filter(Service.title.contains(category)).all()
    all_services.update(services)
    services = Service.query.filter(Service.description.contains(search_query)).all()
    all_services.update(services)
    services = Service.query.filter(Service.provider.contains(search_query)).all()
    all_services.update(services)

    services = list(all_services)

    if sort == "Ascending":
        services = sorted(services, key=lambda x: x.title)
    else:
        services = sorted(services, reverse=True, key=lambda x: x.title)

    print(services)
    filtered_services = []
    if category != "All":
        for service in services:
            if service.category == category:
                filtered_services.append(service)
        services = filtered_services

    return render_template(
        "search_result.html", services=services, search_query=search_query
    )

    # category = None
    # query = None
    # service_results = []
    # provider_results = []
    # # extract all categories
    # categories = Service.query.with_entities(Service.category).distinct().all()
    # categories = [category[0] for category in categories]

    # if request.method == "GET":
    #     search_query = request.args.get("search")
    #     search_type = request.args.get("type")
    #     # not default category is required
    #     category = request.args.get("category")
    #     sort = request.args.get("sort", "asc")

    #     print(">>>")
    #     print(search_query)
    #     print(search_type)adfasdfasasd
    #     print(category)
    #     print(sort)
    #     print(">>>")

    #     if search_type == "services":
    #         service_results = Service.query.filter(
    #             Service.title.contains(search_query)
    #         ).all()
    #     else:
    #         provider_results = Provider.query.filter(
    #             Provider.brand_title.contains(search_query)
    #         ).all()

    #     if category:
    #         service_results = (
    #             Service.query.filter(Service.title.contains(search_query))
    #             .filter_by(category=category)
    #             .all()
    #         )

    #     if sort == "asc":
    #         service_results = sorted(service_results, key=lambda x: x.title)
    #         provider_results = sorted(provider_results, key=lambda x: x.brand_title)
    #     else:
    #         service_results = sorted(
    #             service_results, reverse=True, key=lambda x: x.title
    #         )
    #         provider_results = sorted(
    #             provider_results, reverse=True, key=lambda x: x.brand_title
    #         )

    # return render_template(
    #     "search.html",
    #     title="Search Result",
    #     categories=categories,
    #     query=query,
    #     category=category,
    #     services=service_results,
    #     providers=provider_results,
    #     sort_value=sort,
    #     category_value=category,
    # )
