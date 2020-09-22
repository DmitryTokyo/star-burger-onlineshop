from django.db import models
from foodcartapp.models import Product, Restaurant, RestaurantMenuItem
from foodcartapp.models import Order


def get_restaraunt_list(order):
    products = order.products.all()
    restaurants_make_products = []
    for product in products:
        restaurants_make_products.append([restaurant_item.restaurant.name for restaurant_item in product.product.menu_items.all()])

    if len(restaurants_make_products) > 1:
        restaurants = get_restaurants(restaurants_make_products)
        return restaurants
    else:
        return restaurants_make_products[0]


def get_restaurants(restaurants):
    for count in range(1, len(restaurants)):
        restaurants = list(set(restaurants[count-1]) & set(restaurants[count]))
        if len(restaurants) == 0:
            restaurants = list(set(restaurants[count-1] + restaurants[count]))
            return restaurants
        else:
            return restaurants

