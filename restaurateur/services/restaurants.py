from django.forms.models import model_to_dict

from django.db.models import QuerySet
from geopy import distance

from foodcartapp.models import Order, Restaurant, DeliveryLocation


def get_restaurants_and_delivery_distance(  # noqa FNE007
        restaurants_for_order: list[dict],
        order: Order,
        delivery_location_qs: QuerySet,
) -> list[dict[str, str]]:
    for restaurant in restaurants_for_order:
        restaurant['distance'] = get_distance(restaurant, order.address, delivery_location_qs)

    return sorted(restaurants_for_order, key=lambda key: key['distance'])


def get_distance(restaurant: dict, order_address: str, delivery_location_qs: QuerySet) -> str:
    if not restaurant['longitude'] and not restaurant['latitude']:
        restaurant_obj = Restaurant.objects.get(id=restaurant['id'])
        restaurant['longitude'], restaurant['latitude'] = restaurant_obj.coordinates

    filtered_delivery_location = list(filter(lambda l: l['address'] == order_address, delivery_location_qs))
    delivery_location = filtered_delivery_location[0] if filtered_delivery_location else None
    if not delivery_location:
        delivery_location_obj, _ = DeliveryLocation.objects.get_or_create(
            address=order_address,
        )
        delivery_location = model_to_dict(delivery_location_obj)
        delivery_location['longitude'], delivery_location['latitude'] = delivery_location_obj.coordinates

    delivery_distance = distance.distance(
        (restaurant['latitude'], restaurant['longitude']),
        (delivery_location['latitude'], delivery_location['longitude']),
    ).km
    return f'{delivery_distance:.2f} км'
