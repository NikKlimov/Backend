from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .jwt_helper import *
from .permissions import *
from .serializer import *
from .models import *


def get_draft_order(request):
    order = Order.objects.filter(status=1).first()

    if order is None:
        return None

    return order


@api_view(["GET"])
def search_products(request):
    query = request.GET.get("query", "")

    products = Product.objects.filter(status=1).filter(name__icontains=query)

    serializer = ProductSerializer(products, many=True)

    draft_order = get_draft_order(request)

    resp = {
        "products": serializer.data,
        "draft_order_id": draft_order.pk if draft_order else None
    }

    return Response(resp)


@api_view(["GET"])
def get_product_by_id(request, product_id):
    if not Product.objects.filter(pk=product_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    product = Product.objects.get(pk=product_id)
    serializer = ProductSerializer(product, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_product(request, product_id):
    if not Product.objects.filter(pk=product_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    product = Product.objects.get(pk=product_id)
    serializer = ProductSerializer(product, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_product(request):
    Product.objects.create()

    products = Product.objects.filter(status=1)
    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_product(request, product_id):
    if not Product.objects.filter(pk=product_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    product = Product.objects.get(pk=product_id)
    product.status = 5
    product.save()

    products = Product.objects.filter(status=1)
    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_product_to_order(request, product_id):
    if not Product.objects.filter(pk=product_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    product = Product.objects.get(pk=product_id)

    draft_order = get_draft_order(request)

    if draft_order is None:
        draft_order = Order.objects.create()
        draft_order.save()

    if ProductOrder.objects.filter(order=draft_order, product=product).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    cons = ProductOrder.objects.create()
    cons.order = draft_order
    cons.product = product
    cons.save()

    serializer = OrderSerializer(draft_order, many=False)

    return Response(serializer.data)


@api_view(["GET"])
def get_product_image(request, product_id):
    if not Product.objects.filter(pk=product_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    product = Product.objects.get(pk=product_id)

    return HttpResponse(product.image, content_type="image/png")


@api_view(["PUT"])
def update_product_image(request, product_id):
    if not Product.objects.filter(pk=product_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    product = Product.objects.get(pk=product_id)
    serializer = ProductSerializer(product, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
def search_orders(request):
    status_id = int(request.GET.get("status", -1))
    date_start = request.GET.get("date_start", -1)
    date_end = request.GET.get("date_end", -1)

    orders = Order.objects.exclude(status__in=[1, 5])

    if status_id != -1:
        orders = orders.filter(status=status_id)

    if date_start != -1:
        orders = orders.filter(date_formation__gte=parse_datetime(date_start))

    if date_end != -1:
        orders = orders.filter(date_formation__lte=parse_datetime(date_end))

    serializer = OrdersSerializer(orders, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_order_by_id(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_order(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)
    serializer = OrderSerializer(order, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    date_order = request.data.get("date_order")
    if date_order:
        order.date_order = parse_datetime(date_order)

    order.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)

    if order.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = 2
    order.date_formation = timezone.now()
    order.save()

    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order = Order.objects.get(pk=order_id)

    if order.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = request_status
    order.date_complete = timezone.now()
    order.save()

    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_order(request, order_id):
    if not Order.objects.filter(pk=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.get(pk=order_id)

    if order.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status = 5
    order.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_product_from_order(request, order_id, product_id):
    if not ProductOrder.objects.filter(product_id=product_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ProductOrder.objects.get(product_id=product_id, order_id=order_id)
    item.delete()

    order = Order.objects.get(pk=order_id)

    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data["products"])


@api_view(["GET"])
def get_order_product(request, order_id, product_id):
    if not ProductOrder.objects.filter(product_id=product_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ProductOrder.objects.get(product_id=product_id, order_id=order_id)
    return Response(item.value)


@api_view(["PUT"])
def update_order_product(request, order_id, product_id):
    if not ProductOrder.objects.filter(product_id=product_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ProductOrder.objects.get(product_id=product_id, order_id=order_id)

    serializer = ProductOrderSerializer(item, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(user.id)

    user_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }

    response = Response(user_data, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=False, expires=settings.JWT["ACCESS_TOKEN_LIFETIME"])

    return response


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    access_token = create_access_token(user.id)

    message = {
        'message': 'User registered successfully',
        'user_id': user.id,
        "access_token": access_token
    }

    response = Response(message, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=False, expires=settings.JWT["ACCESS_TOKEN_LIFETIME"])

    return response


@api_view(["POST"])
def check(request):
    token = get_access_token(request)

    if token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    if token in cache:
        message = {"message": "Token in blacklist"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    user = CustomUser.objects.get(pk=user_id)
    serializer = CustomUserSerializer(user, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = get_access_token(request)

    if access_token not in cache:
        cache.set(access_token, settings.JWT["ACCESS_TOKEN_LIFETIME"])

    message = {"message": "Вы успешно вышли из аккаунта"}
    response = Response(message, status=status.HTTP_200_OK)

    response.delete_cookie('access_token')

    return response
