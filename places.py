class Place:

    def __init__(self, json_data):
        self.name = json_data["name"]
        self.rating = json_data["rating"]
        self.address = json_data["formatted_address"]
 

    def print_place_information(self):
        print("--------------------------------------------------------------------")
        print("Name: " + self.name)
        print("Google Reviews Rating: " + str(self.rating))
        print("Address: " + self.address)
