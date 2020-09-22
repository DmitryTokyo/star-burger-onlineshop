from django.db import models
from foodcartapp.models import Product, Restaurant, RestaurantMenuItem
from foodcartapp.models import Order

from distance import get_distance


def get_restaraunt_list(order):
    products = order.products.all()
    restaurants_make_products = []
    for product in products:
        restaurants_make_products.append([restaurant_item.restaurant.name for restaurant_item in product.product.menu_items.all()])

    if len(restaurants_make_products) > 1:
        restaurants_list = get_restaurants(restaurants_make_products)
        return add_restaurant_and_coordinates(restaurants_list)
    else:
        restaurants_list = restaurants_make_products[0]
        return add_restaurant_and_coordinates(restaurants_list)


def get_restaurants(restaurants):
    restaurant_list = []
    for count in range(1, len(restaurants)):
        if count == 1:
            restaurants_list = list(set(restaurants[count-1]) & set(restaurants[count]))
            if len(restaurants_list) == 0:
                restaurants_list = list(set(restaurants[count-1] + restaurants[count]))
        else:
            restaurants_list = list(set(restaurants_list) & set(restaurants[count]))
            if len(restaurants_list) == 0:
                restaurants_list = list(set(restaurants_list + restaurants[count]))

    return restaurants_list


def add_restaurant_and_coordinates(restaurants_list):
    restaurants = []
    for restaurant in restaurants_list:
            distance = get_distance(restaurant)
            restaurants.append({
                'name': restaurant,
                'distance': distance
            })
    return restaurants
