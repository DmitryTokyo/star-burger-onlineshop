from http.client import HTTPResponse
from typing import Any

from django import forms
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant
from foodcartapp.models import Order
from restaurateur.services.restaurants import get_restaurants_and_delivery_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя',
        }),
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        }),
    )


class LoginView(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HTTPResponse:
        form = Login()
        return render(request, 'login.html', context={
            'form': form,
        })

    def post(self, request: HttpRequest) -> HTTPResponse:
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:
                    return redirect('restaurateur:RestaurantView')
                return redirect('start_page')

        return render(request, 'login.html', context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user: User) -> bool:
    return user.is_staff


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request: HttpRequest) -> HTTPResponse:
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability),
        )

    return render(request, template_name='products_list.html', context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request: HttpRequest) -> HTTPResponse:
    return render(request, template_name='restaurants_list.html', context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request: HttpRequest) -> HTTPResponse:
    orders = Order.objects.total_cost()
    order_items = []
    for order in orders:
        restaurants = get_restaurants_and_delivery_distance(order)
        order_items.append({
            'id': order.id,
            'status': order.get_order_status_display(),
            'firstname': order.firstname,
            'lastname': order.lastname,
            'phonenumber': order.phonenumber,
            'address': order.address,
            'cost': order.total_cost,
            'change_url': reverse('admin:foodcartapp_order_change', args=(order.id,), current_app='restaurateur'),
            'comment': order.comment,
            'payment_method': order.payment_method,
            'restaurants': restaurants,
        })

    return render(request, template_name='order_items.html', context={
        'order_items': order_items,
    })
