from rest_framework import serializers
from foodcartapp.models import Order, OrderItem, Banner


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']

    products = OrderItemSerializer(many=True, write_only=True, allow_empty=False, source='order_items')


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['title', 'src', 'description']
