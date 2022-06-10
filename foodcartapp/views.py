from typing import Any

from django.core.signing import Signer, BadSignature
from django.http import JsonResponse
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from foodcartapp.models import Product, OrderItem, Order, Banner
from foodcartapp.serializers import OrderSerializer, BannerSerializer


class BannersListViews(ListAPIView):
    serializer_class = BannerSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsListApiViews(APIView):

    def get(self, request: Request, *args: Any, **kwargs: Any) -> JsonResponse:
        products = Product.objects.select_related('category').available()

        dumped_products = []
        for product in products:
            dumped_product = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'special_status': product.special_status,
                'ingredients': product.ingredients,
                'category': {
                    'id': product.category.id,
                    'name': product.category.name,
                },
                'image': product.image.url,
                'restaurant': {
                    'id': product.id,
                    'name': product.name,
                },
            }
            dumped_products.append(dumped_product)
        return JsonResponse(dumped_products, safe=False, json_dumps_params={
            'ensure_ascii': False,
            'indent': 4,
        })


class RegisterOrderViews(CreateAPIView):
    serializer_class = OrderSerializer

    @transaction.atomic
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        signer = Signer()
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.create(
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data['lastname'],
            phonenumber=serializer.validated_data['phonenumber'],
            address=serializer.validated_data['address'],
            payment_method=serializer.validated_data['payment_method'],
        )

        request.session[f'order_{order.pk}'] = signer.sign(order.pk)

        products_in_order = serializer.validated_data['order_items']
        order_products = [OrderItem(order=order, **fields) for fields in products_in_order]

        for order_product in order_products:
            order_product.product_cost = order_product.product.price

        OrderItem.objects.bulk_create(order_products)

        return Response(serializer.data, status=201)


@api_view(['GET', 'DELETE', 'PATCH'])
def handle_order_detail(request: Request, pk: int) -> Response:  # noqa CFQ004
    signer = Signer()
    try:
        signer.unsign(request.session[f'order_{pk}'])
    except BadSignature:
        message = 'Sorry, but we can recognize your request. Please try again'
        return Response({'message': message}, status=401)

    order = Order.objects.filter(pk=pk).first()
    if not order:
        return Response({'message': 'The order does not exist'}, status=404)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    if request.method == 'DELETE':
        order.delete()
        return Response({'message': 'The order was deleted successfully!'}, status=204)

    if request.method == 'PATCH':
        serializer = OrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
