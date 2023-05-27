import os

import folium
import requests
import logging

polygon_directory = 'polygons/'


def main():
    all_geo_cities = requests.get(
        "https://public.opendatasoft.com/api/records/1.0/search/?dataset=geonames-all-cities"
        "-with-a-population-1000&rows=126&q=&facet=feature_code&facet=cou_name_en&facet=timezone&refine"
        ".cou_name_en=Georgia"
    )

    _map = folium.Map(
        location=[41.6938, 44.8015],
        zoom_start=9,
        tiles="Stamen Terrain"
    )

    fg = folium.FeatureGroup(name='Cities with populations')

    for city in all_geo_cities.json()['records']:
        city = city['fields']
        fg.add_child(
            folium.Marker(
                location=city['coordinates'],
                popup=F"{city['name'].replace('’', '')} - {city['population']}",
                icon=folium.Icon(color='green')
            )
        )

    for file in os.listdir(polygon_directory):
        fg.add_child(
            folium.GeoJson(
                data=open(f'{polygon_directory}{file}', 'r', encoding='utf-8').read()
            )
        )

    _map.add_child(fg)
    _map.save('map.html')
    _map.show_in_browser()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
