from rest_framework import serializers
from foodcartapp.models import Order, OrderProduct, Banner


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'order_products']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['title', 'src', 'description']
