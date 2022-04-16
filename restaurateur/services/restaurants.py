from django.db.models import F
from geopy import distance

from foodcartapp.models import Location, Order


def get_restaurants_and_delivery_distance(order: Order) -> list[dict[str, str]]:  # noqa FNE007
    restaurants = order.items.filter(
        product__menu_items__restaurant__isnull=False,
    ).values(
        name=F('product__menu_items__restaurant__name'),
        restaurant_address=F('product__menu_items__restaurant__address'),
    )

    for restaurant in restaurants:
        restaurant['distance'] = get_distance(restaurant['restaurant_address'], order.address)

    return sorted(restaurants, key=lambda key: key['distance'])


def get_distance(restaurant_address: str, delivery_address: str) -> str:
    location, _ = Location.objects.get_or_create(
        restaurant_address=restaurant_address,
        delivery_address=delivery_address,
    )

    delivery_distance = distance.distance(
        (location.restaurant_lat, location.restaurant_lon),
        (location.delivery_lat, location.delivery_lon),
    ).km
    return f'{delivery_distance:.2f} км'
