from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(CustomUser)
admin.site.register(Order)
admin.site.register(ProductOrder)
