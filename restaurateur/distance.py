import requests
from environs import Env
from geopy import distance

env = Env()
env.read_env()

APIKEY = env('APIKEY')
HOME_LON = env.float('HOME_LON')
HOME_LAT = env.float('HOME_LAT')

def get_distance(place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": APIKEY, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    home_coordinates = (HOME_LAT, HOME_LON)
    restaurant_coordinates = (float(lat), float(lon))
    restaurant_distance = distance.distance(home_coordinates, restaurant_coordinates).km
    return '{:.2f} км.'.format(restaurant_distance)
