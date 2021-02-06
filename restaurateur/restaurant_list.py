from django.db import models
from foodcartapp.models import Product, Restaurant, RestaurantMenuItem
from foodcartapp.models import Order, RestaurantLocation, DeliveryLocation
from geopy import distance
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist

from restaurateur.fetch_coordinates import fetch_coordinates


def get_restaurants_and_distance_from_order(order, delivery_address):
    order_products = order.order_products.all().prefetch_related('product__menu_items__restaurant')
    product_sell_restaurants = []
    for order_product in order_products:
        product_sell_restaurants.append([restaurant_item.restaurant for restaurant_item in order_product.product.menu_items.all()])

    if len(product_sell_restaurants) > 1:
        restaurants = get_restaurants(product_sell_restaurants)
        return get_restaurant_and_distance(restaurants, delivery_address)

    restaurants_list = product_sell_restaurants[0]
    return get_restaurant_and_distance(restaurants_list, delivery_address)


def get_restaurants(restaurants):
    restaurant_list = []
    for count in range(1, len(restaurants)):
        if count == 1:
            restaurants_list = list(set(restaurants[0]) & set(restaurants[count]))
            if len(restaurants_list) == 0:
                restaurants_list = list(set(restaurants[count-1] + restaurants[count]))
        else:
            restaurants_list = list(set(restaurants_list) & set(restaurants[count]))
            if len(restaurants_list) == 0:
                restaurants_list = list(set(restaurants_list + restaurants[count]))

    return restaurants_list


def get_restaurant_and_distance(restaurants_list, delivery_address):
    restaurants = []
    for restaurant in restaurants_list:
        restaurants.append({
            'name': restaurant.name,
            'distance': get_distance(restaurant.address, delivery_address)
        })
    return sorted(restaurants, key=lambda key: key['distance'])


def get_distance(restaurant_address, delivery_address):
    try:
        restaurant_location = RestaurantLocation.objects.get(restaurant_address=restaurant_address)
        restaurant_lon = restaurant_location.restaurant_lon
        restaurant_lat = restaurant_location.restaurant_lat
    except ObjectDoesNotExist:
        restaurant_lon, restaurant_lat = fetch_coordinates(restaurant_address)
        restaurant_location = RestaurantLocation.objects.create(
            restaurant_address = restaurant_address,
            restaurant_lon = restaurant_lon,
            restaurant_lat = restaurant_lat
        )
        restaurant_location.save()

    try:
        delivery_location = DeliveryLocation.objects.get(delivery_address=delivery_address)
        delivery_lon = delivery_location.delivery_lon
        delivery_lat = delivery_location.delivery_lat
    except ObjectDoesNotExist:
        delivery_lon, delivery_lat = fetch_coordinates(delivery_address)
        delivery_location = DeliveryLocation.objects.create(
            delivery_address = delivery_address,
            delivery_lon = delivery_lon,
            delivery_lat = delivery_lat
        )
        delivery_location.save()

    delivery_distance = distance.distance((float(restaurant_lat), float(restaurant_lon)), (float(delivery_lat), float(delivery_lon))).km
    return '{:.2f} км.'.format(delivery_distance)
