+import time
import googlemaps # pip install googlemaps
import pandas as pd # pip install pandas
import config
   
API_KEY = config.API_KEY 
map_client = googlemaps.Client(API_KEY)
business_list = []

def miles_to_meters(miles):
    try:
        return miles * 1_609.344
    except:
        return 0


def get_lat_long(address):
    geocode = map_client.geocode(address=address)
    (lat, lng) = map(geocode[0]['geometry']['location'].get, ('lat', 'lng'))
    return (lat,lng)


def get_business_list(search_string, radius_miles, address):
    (lat, lng) = get_lat_long(address)
    distance = miles_to_meters(radius_miles)
    response = map_client.places_nearby(
        location=(lat, lng),
        keyword=search_string,
        radius=distance
    )   
    business_list.extend(response.get('results'))
    next_page_token = response.get('next_page_token')

    while next_page_token:
        time.sleep(2)
        response = map_client.places_nearby(
            location=(lat, lng),
            keyword=search_string,
            radius=distance,
            page_token=next_page_token
        )   
        business_list.extend(response.get('results'))
        next_page_token = response.get('next_page_token')
    response = filter_response(business_list, search_string)
    return response


def filter_response(busines_list, search_string):
    df = pd.DataFrame(business_list)
    df['url'] = 'https://www.google.com/maps/place/?q=place_id:' + df['place_id']
    df.to_excel('{0}.xlsx'.format(search_string), index=False)
    df1 = df.drop(columns=['geometry', 'opening_hours', 'photos', 'place_id', 'reference', 'plus_code', 'icon', 'icon_background_color','icon_mask_base_uri', 'scope'])
    new_df = df1.head(config.TOP_RESULT_COUNT)
    return new_df.to_dict()
    
