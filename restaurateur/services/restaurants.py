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
        restaurant_lon, restaurant_lat = (
            get_or_create_restaurant_coordinates(restaurant)
            if not restaurant['longitude'] and not restaurant['latitude']
            else restaurant['longitude'], restaurant['latitude'],
        )
        delivery_lon, delivery_lat = get_or_create_delivery_coordinates(order.address, delivery_location_qs)

        restaurant['distance'] = get_distance(
            restaurant_lon=restaurant_lon,
            restaurant_lat=restaurant_lat,
            delivery_lon=delivery_lon,
            delivery_lat=delivery_lat,
        )

    return sorted(restaurants_for_order, key=lambda key: key['distance'])


def get_or_create_restaurant_coordinates(restaurant: dict) -> tuple[float | None, float | None]:
    restaurant_obj = Restaurant.objects.get(id=restaurant['id'])
    longitude, latitude = restaurant_obj.coordinates
    return longitude, latitude


def get_or_create_delivery_coordinates(
        order_address: str,
        delivery_location_qs: QuerySet,
) -> tuple[float | None, float | None]:
    filtered_delivery_location = list(filter(lambda l: l['address'] == order_address, delivery_location_qs))
    delivery_location = filtered_delivery_location[0] if filtered_delivery_location else None
    if not delivery_location:
        delivery_location_obj, _ = DeliveryLocation.objects.get_or_create(
            address=order_address,
        )
        delivery_location = model_to_dict(delivery_location_obj)
        delivery_location['longitude'], delivery_location['latitude'] = delivery_location_obj.coordinates

    return delivery_location['longitude'], delivery_location['latitude']


def get_distance(
        restaurant_lon: float | None,
        restaurant_lat: float | None,
        delivery_lon: float | None,
        delivery_lat: float | None,
) -> str:
    delivery_distance = distance.distance(
        (restaurant_lat, restaurant_lon),
        (delivery_lat, delivery_lon),
    ).km
    return f'{delivery_distance:.2f} км'
