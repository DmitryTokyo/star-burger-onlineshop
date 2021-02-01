from django.db import models
from foodcartapp.models import Product, Restaurant, RestaurantMenuItem
from foodcartapp.models import Order
from geopy import distance
from django.core.cache import cache
from django.db import connection

from restaurateur.fetch_coordinates import fetch_coordinates


def get_restaraunts_and_distance_from_order(order, address):
    order_products = order.order_products.all().prefetch_related('product__menu_items__restaurant')
    restaurants_make_products = []
    for order_product in order_products:
        restaurants_make_products.append([restaurant_item.restaurant.name for restaurant_item in order_product.product.menu_items.all()])

    if len(restaurants_make_products) > 1:
        restaurants_list = get_restaurants_list(restaurants_make_products)
        return get_restaurant_and_distance(restaurants_list, address)

    restaurants_list = restaurants_make_products[0]
    return get_restaurant_and_distance(restaurants_list, address)


def get_restaurants_list(restaurants):
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


def get_restaurant_and_distance(restaurants_list, address):
    restaurants = []
    for restaurant in restaurants_list:
            restaurants.append({
                'name': restaurant,
                'distance': get_distance(restaurant, address)
            })
    return restaurants


def get_distance(restaurant, address):
    try:
        restaurant_lon, restaurant_lat = cache.get(restaurant).split(',')
    except Exception:
        restaurant_lon, restaurant_lat = fetch_coordinates(restaurant)
        cache.set(restaurant, f'{restaurant_lon},{restaurant_lat}')

    try:
        client_lon, client_lat = cache.get(address).split(',')
    except Exception:
        client_lon, client_lat = fetch_coordinates(address)
        cache.set(address, f'{client_lon},{client_lat}')

    restaurant_distance = distance.distance((float(restaurant_lat), float(restaurant_lon)), (float(client_lat), float(client_lon))).km
    return '{:.2f} км.'.format(restaurant_distance)
