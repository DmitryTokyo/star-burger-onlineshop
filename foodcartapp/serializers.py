from rest_framework import serializers
from enumfields.drf.serializers import EnumSupportSerializerMixin
from foodcartapp.models import Order, OrderItem, Banner


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, write_only=True, allow_empty=False, source='order_items')

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products', 'payment_method']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['title', 'src', 'description']
