from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name="home"),
    path('products/<int:product_id>/', product_details),
    path('products/<int:product_id>/delete/', product_delete)
]
