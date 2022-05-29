from json import JSONDecodeError

import requests
from django.conf import settings

from loguru import logger


def fetch_coordinates(place: str) -> tuple[float | None, float | None]:
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    params = {'geocode': place, 'apikey': settings.YANDEX_MAP_APIKEY, 'format': 'json'}
    response = requests.get(base_url, params=params)
    if not response.ok:
        logger.bind(
            user_place=place,
            status_code=response.status_code,
            response_content=str(response.content),
        ).error('Error with fetching geocoder response')
        return None, None
    try:
        places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    except JSONDecodeError:
        logger.bind(
            user_place=place,
            status_code=response.status_code,
            response_content=str(response.content),
        ).error('Error with deserialization geocoder result')
        return None, None
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    logger.bind(
        user_place=place,
        status_code=response.status_code,
        response_content=str(response.content),
    ).debug('Coordinates was fetched')
    return lon, lat
