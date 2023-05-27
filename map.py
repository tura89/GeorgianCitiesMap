"""Generate map of Georgia with popups and layers about its population."""
import json
import os

import logging
import folium
import requests

POLYGON_DIRECTORY = 'polygons/'


def population_brackets(pop):
    """Assign fillColor Color based on the population."""
    pop = int(pop['geometry']['population'])
    color = 'white'
    if pop < 1000000:
        color = 'green'
    if pop < 50000:
        color = 'yellow'
    if pop < 25000:
        color = 'orange'
    if pop < 10000:
        color = 'red'
    return {'fillColor': color}


def main():
    """Generate the map using data from polygons directory."""

    _map = folium.Map(
        location=[41.6938, 44.8015],
        zoom_start=9,
    )

    # populate the map with city markers
    city_layer = folium.FeatureGroup(name='Cities with populations')

    all_geo_cities = requests.get(
        "https://public.opendatasoft.com/api/records/1.0/search/?dataset=geonames-all-cities"
        "-with-a-population-1000&rows=126&q=&facet=feature_code&facet=cou_name_en&facet=timezone"
        "&refine.cou_name_en=Georgia", timeout=30
    )

    for city in all_geo_cities.json()['records']:
        city = city['fields']
        city_layer.add_child(
            folium.Marker(
                location=city['coordinates'],
                popup=F"{city['name'].replace('’', '')} - {city['population']}",
                icon=folium.Icon(color='green')
            )
        )

    # populate the map with municipality polygons
    municipality_layer = folium.FeatureGroup(name='Municipalities by populations')
    for file in os.listdir(POLYGON_DIRECTORY):
        with open(f'{POLYGON_DIRECTORY}{file}', 'r', encoding='utf-8') as json_file:
            data = json_file.read()

        geojson = folium.GeoJson(
            data=data,
            style_function=population_brackets,
            popup=lambda x: x['geometry']['population']
        )

        population = json.loads(data)['population']
        folium.Popup(population).add_to(geojson)

        municipality_layer.add_child(geojson)

    _map.add_child(city_layer)
    _map.add_child(municipality_layer)
    _map.add_child(folium.LayerControl())

    _map.save('map.html')
    _map.show_in_browser()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
