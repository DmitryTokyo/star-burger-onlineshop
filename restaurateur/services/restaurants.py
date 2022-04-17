from typing import Mapping
from django.forms.models import model_to_dict

from django.db.models import QuerySet
from geopy import distance

from foodcartapp.models import Location, Order


def get_restaurants_and_delivery_distance(
        restaurants_data: list[dict],
        order: Order,
        location_qs: QuerySet,
) -> list[dict[str, str]]:  # noqa FNE007
    print(location_qs)
    for restaurant in restaurants_data:
        restaurant['distance'] = get_distance(restaurant['address'], order.address, location_qs)

    return sorted(restaurants_data, key=lambda key: key['distance'])


def get_distance(restaurant_address: str, delivery_address: str, location_qs: QuerySet) -> str:
    filtered_location = list(filter(lambda l: l['restaurant_address'] == restaurant_address and l['delivery_address'] == delivery_address, location_qs))
    location = filtered_location[0] if filtered_location else None
    if not location:
        location_obj, _ = Location.objects.create(
            restaurant_address=restaurant_address,
            delivery_address=delivery_address,
        )
        location = model_to_dict(location_obj)

    delivery_distance = distance.distance(
        (location['restaurant_lat'], location['restaurant_lon']),
        (location['delivery_lat'], location['delivery_lon']),
    ).km
    return f'{delivery_distance:.2f} км'
