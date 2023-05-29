"""Script to get polygon data for the map from openstreetmaps.

Data is retrieved for each municipality in municipalities.txt and written to
the respective json file in polygons directory.
"""
import logging
import json
import os
import requests
from config import POLYGON_DIRECTORY, DATA_DIRECTORY, MUNICIPALITIES_FILENAME


def get_location_id(location):
    """Get the id of the location from openstreetmap."""
    # some regions can't be looked up by name, in which case their id is used
    if any(char.isdigit() for char in location):
        return location

    url = F'https://nominatim.openstreetmap.org/search.php?q={location}&format=jsonv2'
    response = requests.get(url, timeout=10)
    resp_json = response.json()

    if not resp_json:
        return None

    if isinstance(resp_json, list):
        resp_json = resp_json[0]

    return resp_json['osm_id']


def get_polygon(location):
    """Get polygon data from openstreetmaps."""
    logging.info("getting id data for %s", location)
    osm_id = get_location_id(location)

    js_file = f'{POLYGON_DIRECTORY}{osm_id}.json'

    # download not needed if the data is already present
    if os.path.exists(js_file):
        logging.info("data for %s - %s exists, skipping", osm_id, location)
        return None, None

    # request to generate the polygon
    p_url = F'http://polygons.openstreetmap.fr/?id={osm_id}'
    requests.get(p_url, timeout=15)

    # request to get the polygon
    p_url = F'http://polygons.openstreetmap.fr/get_geojson.py?id={osm_id}&params=0'
    logging.info("Trying to get data for %s, url:\n%s", osm_id, p_url)
    response = requests.get(p_url, timeout=15)
    try:
        return response.json(), osm_id
    except requests.exceptions.JSONDecodeError:
        return None, None


def main():
    """Get polygons for municipalities and write them to polygons directory."""
    logging.basicConfig(level=logging.INFO)

    # LIST OF MUNICIPALITIES W/ POPULATIONS
    # list originally from
    # https://en.wikipedia.org/wiki/List_of_municipalities_in_Georgia_(country)#List_of_municipalities_as_of_2019
    # modified to match municipalities as they appear on https://nominatim.openstreetmap.org/
    with open(F'{DATA_DIRECTORY}{MUNICIPALITIES_FILENAME}', 'r', encoding='utf-8') as municipalities_file:
        municipalities = municipalities_file.read().splitlines()

    for municipality in municipalities:
        m_name = municipality.split(' - ')[0]
        data, osm_id = get_polygon(m_name)

        if not data or not osm_id:
            continue

        data['population'] = municipality.split(' - ')[1]
        js_file = f'{POLYGON_DIRECTORY}{osm_id}.json'

        with open(js_file, 'w', encoding='utf-8') as file:
            logging.info("writing data for %s.", osm_id)
            json.dump(data, file)


if __name__ == '__main__':
    main()
