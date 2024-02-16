import random

from django.core import management
from django.core.management.base import BaseCommand
from ...models import *
from .utils import random_date, random_timedelta


def add_products():
    Product.objects.create(
        name="Декларирование товаров",
        description="Товары для личного пользования не превышающие 10000 ервро и весом не более 10 кг.",
        price=3000,
        image="products/1.jpg"
    )

    Product.objects.create(
        name="Декларирование ценностей",
        description="Перемещение культурных ценностей физическими лицами через таможенную границу Перечень культурных ценностей, документов национальных архивных фондов и оригиналов архивных документов, подлежащих контролю при перемещении через таможенную границу Российской Федерации.",
        price=100000,
        image="products/2.jpg"
    )

    Product.objects.create(
        name="Декларирование валют",
        description="Со 2 марта 2022 года временно запрещено вывозить валюту свыше 10 тыс. долл. США. Соответствующий Указ Президента РФ опубликован 1 марта 2022 года. Согласно документу со 2 марта 2022 года запрещено вывозить из РФ наличную иностранную валюту и денежные инструменты в иностранной валюте в сумме",
        price=2000,
        image="products/3.jpg"
    )

    Product.objects.create(
        name="Декларирование транспортных средств",
        description="Согласно ст. 260 ТК ЕАЭС транспортные средства для личного пользования (за исключением ТС, зарегистрированных в странах ЕАЭС), перемещаемые через таможенную границу ЕАЭС любым способом, для целей выпуска в свободное обращение",
        price=3000,
        image="products/4.jpg"
    )

    Product.objects.create(
        name="Декларирование медицинских товаров",
        description="Медицинская аппаратура и лекарственные средства.",
        price=1200,
        image="products/5.jpg"
    )

    print("Услуги добавлены")


def add_orders():
    owners = CustomUser.objects.filter(is_superuser=False)
    moderators = CustomUser.objects.filter(is_superuser=True)

    if len(owners) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    products = Product.objects.all()

    for _ in range(30):
        order = Order.objects.create()
        order.apartment = random.randint(1, 255)
        order.status = random.randint(2, 5)

        if order.status in [3, 4]:
            order.date_complete = random_date()
            order.date_formation = order.date_complete - random_timedelta()
            order.date_created = order.date_formation - random_timedelta()
            order.moderator = random.choice(moderators)
        else:
            order.date_formation = random_date()
            order.date_created = order.date_formation - random_timedelta()

        order.owner = random.choice(owners)

        for i in range(random.randint(1, 3)):
            try:
                item = ProductOrder.objects.create()
                item.order = order
                item.product = random.choice(products)
                item.count = random.randint(1, 5)
                item.save()
            except Exception as e:
                print(e)

        order.save()

    print("Заявки добавлены")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        management.call_command("clean_db")
        management.call_command("add_users")

        add_products()
        add_orders()









