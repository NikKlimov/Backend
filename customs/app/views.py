from django.db import connection
from django.shortcuts import render, redirect

from .models import *


def index(request):
    query = request.GET.get("query", "")
    products = Product.objects.filter(name__icontains=query).filter(status=1)

    context = {
        "query": query,
        "products": products
    }

    return render(request, "home_page.html", context)


def product_details(request, product_id):
    context = {
        "product": Product.objects.get(id=product_id)
    }

    return render(request, "product_page.html", context)


def product_delete(request, product_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE app_product SET status = 2 WHERE id = %s", [product_id])

    return redirect("/")
