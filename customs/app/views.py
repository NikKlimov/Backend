from django.shortcuts import render


db = {
    "products": [
        {
            "id": 1,
            "name": "Декларирование товаров",
            "description": "Товары для личного пользования не превышающие 10000 ервро и весом не более 10 кг.",
            "price": 3000
        },
        {
            "id": 2,
            "name": "Декларирование ценностей",
            "description": "Перемещение культурных ценностей физическими лицами через таможенную границу Перечень культурных ценностей, документов национальных архивных фондов и оригиналов архивных документов, подлежащих контролю при перемещении через таможенную границу Российской Федерации.",
            "price": 100000
        },
        {
            "id": 3,
            "name": "Декларирование валют",
            "description": "Со 2 марта 2022 года временно запрещено вывозить валюту свыше 10 тыс. долл. США. Соответствующий Указ Президента РФ опубликован 1 марта 2022 года. Согласно документу со 2 марта 2022 года запрещено вывозить из РФ наличную иностранную валюту и денежные инструменты в иностранной валюте в сумме.",
            "price": 2000
        },
        {
            "id": 4,
            "name": "Декларирование транспортных средств",
            "description": "Согласно ст. 260 ТК ЕАЭС транспортные средства для личного пользования (за исключением ТС, зарегистрированных в странах ЕАЭС), перемещаемые через таможенную границу ЕАЭС любым способом, для целей выпуска в свободное обращение.",
            "price": 3000
        },
        {
            "id": 5,
            "name": "Декларирование медицинских товаров",
            "description": "Медицинская аппаратура и лекарственные средства.",
            "price": 1200
        }
    ]
}


def getProducts():
    return db["products"]


def getProductById(product_id):
    for product in db["products"]:
        if product["id"] == product_id:
            return product


def searchProducts(product_name):
    products = getProducts()

    res = []

    for product in products:
        if product_name.lower() in product["name"].lower():
            res.append(product)

    return res


def index(request):
    query = request.GET.get("query", "")
    products = searchProducts(query)

    context = {
        "products": products,
        "query": query
    }

    return render(request, "home_page.html", context)


def product(request, product_id):
    context = {
        "id": product_id,
        "product": getProductById(product_id),
    }

    return render(request, "product_page.html", context)

