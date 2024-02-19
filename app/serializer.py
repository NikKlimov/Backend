from rest_framework import serializers

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'email', 'is_moderator')


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    owner = CustomUserSerializer(read_only=True, many=False)
    moderator = CustomUserSerializer(read_only=True, many=False)

    def get_products(self, order):
        items = ProductOrder.objects.filter(order=order)
        return ProductSerializer([item.product for item in items], many=True).data

    class Meta:
        model = Order
        fields = "__all__"


class OrdersSerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer(read_only=True, many=False)
    moderator = CustomUserSerializer(read_only=True, many=False)

    class Meta:
        model = Order
        fields = "__all__"


class ProductOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = "__all__"


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'name')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            name=validated_data['name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)