+from flask import Flask, render_template, request, redirect, Response
import json
import nearby_places

app = Flask(__name__)

@app.route('/')
def output():
	return render_template('index.html', name='Joe')


@app.route('/ILoveCoffee', methods = ['POST'])
def searchPlaces():
    data = request.json
    search_string = data["search_string"]
    radius_miles = data["radius_miles"]
    address = data["address"]
    business_list = nearby_places.get_business_list(search_string, radius_miles, address)
    result = json.dumps(business_list)
    return result


if __name__ == '__main__':
	# run!
	app.run(debug=True)
