# import required packages
from place import Place
import urllib.request
import json

# search according to the zip code
def get_search():
    location_name = input("Enter zip code: ")
    return location_name.replace(" ", "+")


# get request from api
def return_get(location_name):
    key = "API_KEY"
    return "https://maps.googleapis.com/maps/api/place/textsearch/json?query=Cafe+coffee+near+" \
           + location_name.replace(" ", "+") + "&key=" + key

# request the data and decode according to the required encoding (already present)
def places_api_request(request_url):
    web_data = urllib.request.urlopen(request_url)
    data = web_data.read()
    encoding = web_data.info().get_content_charset('utf-8')
    return json.loads(data.decode(encoding))

##Ritika worked on lines 26-57
# the places list with a filter, 
def init_places_list(json_data):
    places = []

    if len(json_data["results"]) > 0:
        for cafe_data in json_data["results"]:
            places.append(Place(cafe_data))

    return places

# Collect the data and print it according to the places class
def display_cafes(places_list):
    if len(places_list) > 0:
        for cafe in places_list:
            cafe.print_place_information()
    else:
        print("No places found")

# main file to run the complete process
def main():
    location = get_search()
    request_url = return_get(location)
    json_data = places_api_request(request_url)

    places_list = init_places_list(json_data)

    display_cafes(places_list)

# main file to run by default
if __name__ == '__main__':
  main()
#We went through the older codes and worked on the last codes created to get a refined version of our final codes.
