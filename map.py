import folium
import requests
import pandas as pd


def get_polygon(location):
    url = F'https://nominatim.openstreetmap.org/search.php?q={location}&format=jsonv2'
    response = requests.get(url)
    js = response.json()
    if not js:
        return None
    osm_id = js[0]['osm_id']

    p_url = F'http://polygons.openstreetmap.fr/get_geojson.py?id={osm_id}&params=0'
    response = requests.get(p_url)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as ex:
        return None


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

    # GET LIST OF MUNICIPALITIES
    muns = pd.read_html(
        'https://en.wikipedia.org/wiki/List_of_municipalities_in_Georgia_(country)#List_of_municipalities_as_of_2019'
    )[2]

    muns = muns.loc[muns['Municipality as of 2019'].str.contains('^[0-9]+')]
    muns[['m1', 'municipalities']] = muns['Municipality as of 2019'].str.split('.', expand=True)

    for mun in muns['municipalities']:
        # clean up the names
        mun = mun[1:] # remove first whitespace
        if mun[-2] == ' ':
            mun = mun[:-2] # remove wikipedia indices
        mun = mun.replace(', City of', '')
        mun = mun.replace(' ', '+')
        polygon = get_polygon(mun)

        if polygon:
            fg.add_child(
                folium.GeoJson(data=polygon)
            )

    _map.add_child(fg)
    _map.save('map.html')
    _map.show_in_browser()


if __name__ == '__main__':
    main()
