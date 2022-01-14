from geopy import distance

from foodcartapp.models import Location


def get_restaurants_and_delivery_distance(order, delivery_address):
    order_items = order.order_items.all().prefetch_related('product__menu_items__restaurant')
    product_sell_restaurants = []
    for order_item in order_items:
        product_sell_restaurants.append(
            [
                restaurant_item.restaurant
                for restaurant_item
                in order_item.product.menu_items.all()
            ]
        )

    if len(product_sell_restaurants) > 1:
        restaurants = sort_restaurants_by_products(product_sell_restaurants)
        return get_restaurants_and_distance(restaurants, delivery_address)

    restaurants_list = product_sell_restaurants[0]
    return get_restaurants_and_distance(restaurants_list, delivery_address)


def sort_restaurants_by_products(restaurants):
    restaurants_list = []
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


def get_restaurants_and_distance(restaurants_list, delivery_address):
    restaurants = []
    for restaurant in restaurants_list:
        restaurants.append({
            'name': restaurant.name,
            'distance': get_distance(restaurant.address, delivery_address)
        })
    return sorted(restaurants, key=lambda key: key['distance'])


def get_distance(restaurant_address, delivery_address):
    location = Location.objects.get_or_create(restaurant_address=restaurant_address, delivery_address=delivery_address)

    delivery_distance = distance.distance(
        (float(location.restaurant_lat), float(location.restaurant_lon)),
        (float(location.delivery_lat), float(location.delivery_lon))
    ).km
    return '{:.2f} км.'.format(delivery_distance)
