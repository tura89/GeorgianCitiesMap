import logging
import requests
import json
import os
from map import polygon_directory


def get_polygon(location):
    logging.info(f"getting id data for {location}")
    url = F'https://nominatim.openstreetmap.org/search.php?q={location}&format=jsonv2'

    if any(char.isdigit() for char in location):
        url = F'https://nominatim.openstreetmap.org/details.php?osmtype=R&osmid={location}' \
              F'&class=boundary&addressdetails=1&hierarchy=0&group_hierarchy=1&format=json'

    response = requests.get(url)
    js = response.json()
    if not js:
        return None, None

    if isinstance(js, list):
        js = js[0]

    osm_id = js['osm_id']
    js_file = f'{polygon_directory}{osm_id}.json'

    if os.path.exists(js_file):
        logging.info(f"data for {osm_id} - {location} exists, skipping")
        return None, None

    p_url = F'http://polygons.openstreetmap.fr/?id={osm_id}'
    requests.get(p_url)
    p_url = F'http://polygons.openstreetmap.fr/get_geojson.py?id={osm_id}&params=0'
    logging.info(f"Tried getting data for {osm_id}, url:\n{p_url}")
    response = requests.get(p_url)
    try:
        return response.json(), osm_id
    except requests.exceptions.JSONDecodeError as ex:
        return None, None

def main():
    logging.basicConfig(level=logging.INFO)

    # GET LIST OF MUNICIPALITIES W/ POPULATIONS
    # list originally from
    # https://en.wikipedia.org/wiki/List_of_municipalities_in_Georgia_(country)#List_of_municipalities_as_of_2019
    # modified to match municipalities as they appear on https://nominatim.openstreetmap.org/
    with open('municipalities.txt', 'r') as municipalities_file:
        municipalities = municipalities_file.read().splitlines()

    for municipality in municipalities:
        m_name = municipality.split(' - ')[0]
        data, osm_id = get_polygon(m_name)

        if not data or not osm_id:
            continue

        data['population'] = municipality.split(' - ')[1]
        js_file = f'{polygon_directory}{osm_id}.json'

        with open(js_file, 'w', encoding='utf-8') as file:
            logging.info(f"writing data for {osm_id}.")
            json.dump(data, file)
