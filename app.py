from flask import Flask, render_template, request, jsonify
import peewee as pw
import json
import urllib.request

myDB = pw.MySQLDatabase('kyan', host = 'mysql.pokegosecrets.com', user = 'kyan', password = 'kyankyan')

app = Flask(__name__)

SITE_KEY = '6LeBmCcUAAAAAPr5kKa_AKPr8UWNCkht3CHCBkNf'
SECRET_KEY = '6LeBmCcUAAAAAPQD-eCLE2DhWBgIkiK8FJK10EFC'


class BaseModel(pw.Model):
    class Meta:
        database = myDB


class Country(BaseModel):
    country_name = pw.CharField(unique=True, max_length=50)

    class Meta:
        order_by = ('country_name',)


class State(BaseModel):
    country = pw.ForeignKeyField(Country, related_name='states', null=True)
    state_name = pw.CharField(max_length=50)

    class Meta:
        order_by = ('state_name',)


class City(BaseModel):
    state = pw.ForeignKeyField(State, related_name='cities', null=True)
    city_name = pw.CharField(max_length=50)

    class Meta:
        order_by = ('city_name',)


class Content(BaseModel):
	city = pw.ForeignKeyField(City, related_name='contents', null=True)
	title = pw.CharField(max_length=255)
	your_name = pw.CharField(max_length=50)
	ad_type = pw.CharField()
	payment_type = pw.CharField()
	website = pw.TextField()
	price = pw.CharField()
	currency = pw.CharField()
	countries = pw.CharField()
	states = pw.CharField(null=True)
	check_ads = pw.BooleanField()
	captcha = pw.TextField()

	class Meta:
		order_by = ('your_name',)


@app.route('/create_database/')
def create_tables():
    myDB.get_conn()
    myDB.create_tables([Country, State, City, Content])
    return('Database completed')

@app.route('/new-ad/')
def upload():
	address = {}
	states = []
	countries = []
	cities = []
	for iterable in State.select():
		states.append(iterable)

	for iterable in Country.select():
		countries.append(iterable)

	for iterable in City.select():
		cities.append(iterable)

	
	address = {'states' : states, 'countries' : countries, 'cities' : cities}
	return render_template('new-ad.html', address = address)


@app.route('/ajaxData/', methods = ['POST'])
def ajaxData():
	adTitle=request.json['adTitle']
	jobTitle=request.json['jobTitle']
	adType=request.json['adType']
	payType=request.json['payType']
	website=request.json['website']
	adPrice=request.json['adPrice']
	currency=request.json['currency']
	country=request.json['country']
	state=request.json['state']
	city=request.json['city']
	adDetail=request.json['adDetail']

	print(adPrice)

	result = Content.insert(
		title = adTitle,
		your_name = jobTitle,
		ad_type = adType,
		payment_type = payType,
		website = website,
		price = adPrice,
		currency = currency,
		city = city,
		countries = country,
		states = state,
		captcha=adDetail).execute()
		
	return jsonify(result = result)


@app.route('/getStates/', methods = ['POST'])
def getStates():
	countryId = request.json['country']
	states = []
	for state in State.select().where(State.country == countryId):
		print (state.state_name)
		states.append({
			"id" : state.id,
			"state_name" : state.state_name
		})

	return jsonify(states = states)

@app.route('/getCities/', methods = ['POST'])
def getCities():
	stateId = request.json['state']
	cities = []
	for city in City.select().where(City.state == stateId):
		cities.append({
			"id" : city.id,
			"city_name" : city.city_name
		})

	return jsonify(cities = cities)

@app.route('/deleteCity/', methods = ["POST"])
def deleteCity():
	cityId = request.json["id"]
	query = City.delete().where(City.id == cityId)
	result = query.execute()
	return jsonify(result = result)

@app.route('/cities/')
def showCities():
	cities = []
	for city in City.select():
		cities.append({
			"id" : city.id,
			"city_name" : city.city_name
		})

	return render_template('cities.html', cities = cities)

@app.before_request
def _db_connect():
	myDB.connect()

@app.teardown_request
def _db_close(exc):
	if not myDB.is_closed():
		myDB.close()

if __name__ == '__main__':
    
    app.debug = True
    app.run()