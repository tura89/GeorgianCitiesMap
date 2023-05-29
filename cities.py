"""Get data about cities of Georgia."""
import pandas as pd
import requests
import time
import logging
from config import DATA_DIRECTORY, CITIES_FILENAME


def get_city(data, city):
    """Get the most likely entry."""
    for entry in data:
        if entry['type'] in ['town', 'city']:
            return entry

    return data[0]


def get_coordinates(city, n_tries=3):
    """Get coordinates of the city."""
    target_url = F'https://nominatim.openstreetmap.org/search?q={city}&format=json'

    try:
        logging.info("Getting data for %s", city)
        data = requests.get(target_url, timeout=10).json()
        data = get_city(data, city)
        logging.info("Returning coordinates for %s", city)
        return data['lat'], data['lon']
    except requests.exceptions.ReadTimeout as ex:
        time.sleep(5)
        get_coordinates(city, n_tries-1) if n_tries > 1 else None

    logging.info("Couldn't retrieve coordinates for %s", city)
    return None


def get_cities():
    """Get all cities of Georgia."""
    wiki_page = 'https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Georgia_(country)'
    df = pd.read_html(wiki_page)[0]

    df['coordinates'] = df['Name'].apply(func=get_coordinates)
    df[['lat', 'lon']] = pd.DataFrame(df['coordinates'].tolist(), index=df.index)

    del df['Name in Georgian']
    del df['Population 1989']
    del df['Population 2002']
    del df['Administrative Region']
    del df['Rank']
    del df['coordinates']

    df.rename(
        columns={
            'Name': 'name',
            'Population 2020': 'population'
        },
        inplace=True
    )

    return df


def get_settlements():
    """Get all settlements (dabas) of Georgia."""
    wiki_page = 'https://en.wikipedia.org/wiki/Daba_(settlement)#List_of_daba_in_Georgia'
    df = pd.read_html(wiki_page)[1]

    df['coordinates'] = df['Daba'].apply(func=get_coordinates)
    df[['lat', 'lon']] = pd.DataFrame(df['coordinates'].tolist(), index=df.index)

    del df['Unnamed: 0']
    del df['Status granted']
    del df['District/Municipality']
    del df['Region or autonomous republic']
    del df['Note']
    del df['coordinates']

    df.rename(
        columns={
            'Daba': 'name',
            'Population (2002)': 'population'
        },
        inplace=True
    )

    df = df[df['population'] != '-']
    df = df[df['population'].astype(int) > 500]

    return df


def main():
    """Get data about cities of Georgia and write them to cities.txt."""
    cities = get_cities()
    settlements = get_settlements()

    locations = pd.concat([cities, settlements])
    locations.to_csv(f'{DATA_DIRECTORY}{CITIES_FILENAME}')



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
