import datetime
import math
import random
from flask import Flask
from flask import request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.secret_key = "Secret Key"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bikes.sqlite3"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sharedbike.db"
app.config["SECRET_KEY"] = "43142341542315"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# pip install --upgrade python-socketio==4.6.0
# pip install --upgrade python-engineio==3.13.2
# pip install --upgrade Flask-SocketIO==4.3.1
# pip install pyOpenSSL

# customer database table
class Customer(db.Model):
    __tablename__ = "customer"
    id = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(120), nullable = False)
    money = db.Column(db.Float)
    bike_id = db.Column(db.Integer, nullable = True)

    def __init__(self, id, password, money, bike_id = ""):
        self.id = id
        self.password = password
        self.money = money
        self.bike_id = bike_id


# operator database table
class Operator(db.Model):
    __tablename__ = "operator"
    id = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(120), nullable = False)

    def __init__(self, id, password):
        self.id = id
        self.password = password


# manager database table
class Manager(db.Model):
    __tablename__ = "manager"
    id = db.Column(db.String(20), primary_key = True)
    password = db.Column(db.String(120), nullable = False)

    def __init__(self, id, password):
        self.id = id
        self.password = password


# bike database table
class Bikes(db.Model):
    __tablename__ = "bikes"
    id = db.Column(db.Integer, primary_key = True)
    source = db.Column(db.String(50))
    latitude = db.Column(db.Numeric)
    longitude = db.Column(db.Numeric)
    condition = db.Column(db.String(10))
    status = db.Column(db.String(20))
    brand = db.Column(db.String(20))

    def __init__(self, id, source, latitude, longitude, condition, status, brand = ""):
        self.id = id
        self.source = source
        self.latitude = latitude
        self.longitude = longitude
        self.condition = condition
        self.status = status
        self.brand = brand


# rent record database table
class RentRecords(db.Model):
    __tablename__ = "rentRecords"
    rentID = db.Column(db.Integer, primary_key = True)
    customerID = db.Column(db.String(20))
    bikeID = db.Column(db.Integer)
    ridingDuration = db.Column(db.Integer)
    cost = db.Column(db.Float)
    recordTime = db.Column(db.DateTime)
    distance = db.Column(db.Float)

    def __init__(self, rentID, customerID, bikeID, ridingDuration, cost, recordTime = datetime.datetime.now(),
                 distance = 0):
        self.rentID = rentID
        self.customerID = customerID
        self.bikeID = bikeID
        self.ridingDuration = ridingDuration
        self.cost = cost
        self.recordTime = recordTime
        self.distance = distance


# Bike Brands
bikeBrand = ["Aima", "Xiaoniu", "Jieante", "Meilida", "Feige", "Amini"]
rentID = 464616


# login page
@app.route('/', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop("user_id", None)
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        usertype = request.form.get("user", None)
        if usertype:
            if usertype == "1":
                customer_info = Customer.query.filter_by(id=username).first()
                if customer_info is None:
                    print("user did not exist")
                else:
                    if customer_info.password == password:
                        session['user_id'] = username
                        session["user_type"] = 1

                        return render_template("micky_map2.html", username = customer_info.id)
            elif usertype == "2":
                operator_info = Operator.query.filter_by(id = username).first()
                if operator_info is None:
                    print("user did not exist")
                else:
                    if operator_info.password == password:
                        session['user_id'] = username
                        session["user_type"] = 2
                    return redirect(url_for("operator"))
            elif usertype == "3":
                manager_info = Manager.query.filter_by(id = username).first()
                if manager_info is None:
                    print("user did not exist")
                else:
                    if manager_info.password == password:
                        session['user_id'] = username
                        session["user_type"] = 3
                    return redirect(url_for("manager"))
    return render_template("index.html")


# register page
@app.route("/register", methods = ["POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        exist = Customer.query.filter_by(id = username).first()
        if exist:
            return render_template("index.html", exist = username)
        else:
            password = request.form["password"]
            register_data = Customer(username, password, 0)
            db.session.add(register_data)
            db.session.commit()
            return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


# customer page
@app.route("/micky_map")
def micky_map():
    return render_template("micky_map2.html")


# operator page
@app.route("/operator")
def operator():
    all_info = Bikes.query.all()
    return render_template("operator.html", bikes = all_info)


# insert function of operator page
@app.route('/insert', methods = ["POST"])
def insert():
    bikeid = request.form["bikeid"]
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    source = "{:.1f} {:.1f}".format(float(latitude), float(longitude))
    brand = request.form["brand"]
    condition = request.form["condition"]
    status = request.form["status"]
    insert_data = Bikes(bikeid, str(source), latitude, longitude, condition, status, brand)
    db.session.add(insert_data)
    db.session.commit()
    return redirect(url_for("operator"))


# remove function of operator page
@app.route('/remove/<id>', methods = ["GET", "POST"])
def remove(id):
    delete_data = Bikes.query.get(id)
    db.session.delete(delete_data)
    db.session.commit()
    return redirect(url_for("operator"))


# edit function of operator page
@app.route('/edit', methods = ["POST"])
def edit():
    id = request.form.get("id")
    bike_info = Bikes.query.get(id)
    bike_info.latitude = request.form['latitude']
    bike_info.longitude = request.form['longitude']
    bike_info.brand = request.form["brand"]
    bike_info.condition = request.form['condition']
    bike_info.status = request.form["status"]
    db.session.commit()
    return redirect(url_for("operator"))


# manager page
@app.route("/manager")
def manager():
    # bike information chart
    all_info = Bikes.query.all()
    brand = {}
    for bike in all_info:
        if not bike.brand in brand:
            brand[bike.brand] = 1
        else:
            brand[bike.brand] += 1
    list_brand = []
    list_brand.append(list(brand.keys()))
    list_brand.append(list(brand.values()))
    # bike condition chart
    good = 0
    bad = 0
    for bike in all_info:
        if bike.condition == 'Good':
            good += 1
        else:
            bad += 1
    condition = [good,bad]
    # bike available chart
    available = 0
    unavailable = 0
    for bike in all_info:
        if bike.status == 'Available':
            available += 1
        else:
            unavailable += 1
    bikes_available = [good, bad]
    # orders
    orders_time = [order.recordTime.strftime('%Y-%m-%d') for order in RentRecords.query.all()]
    orders_id = [order.rentID for order in RentRecords.query.all()]
    orders_customer = [order.customerID for order in RentRecords.query.all()]
    orders_bikeid = [order.bikeID for order in RentRecords.query.all()]
    orders_ride = [order.ridingDuration for order in RentRecords.query.all()]
    orders_cost = [order.cost for order in RentRecords.query.all()]

    return render_template("manager.html", bikes_brand = list_brand, bikes_condition = condition, available = bikes_available,
                           orders_id = orders_id, orders_time = orders_time, orders_customer = orders_customer, orders_bikeid = orders_bikeid,
                           orders_ride = orders_ride, orders_cost = orders_cost)


# get bike info from database and transmit it to front end
@app.route("/getlnglat", methods = ['POST'])
def getLngLat():
    lat = float(request.form['lat'])
    lng = float(request.form['lng'])

    source = str("{:.1f} {:.1f}".format(lat, lng))
    print(source)
    rs = Bikes.query.filter(Bikes.source == source).all()
    print("rs:", rs)
    if not rs:
        bikeInfo = generateRandomBikes(source, lat, lng)
    else:
        bikeInfo = getBikesFromDatabase(source)
    print("bikeInfo", bikeInfo)
    return jsonify(bikeInfo)


# generate random bikes based on users current locations(for test).
# paramter: source, user location latitude, user location longitude
# return: bike information list
def generateRandomBikes(source, lat, lon):
    bikeInfo = [];

    for i in range(0, 20, 1):
        id = random.randint(100000, 1000000)
        bike_info = Bikes.query.get(id)
        while bike_info:
            id = random.randint(100000, 1000000)
            bike_info = Bikes.query.get(id)
        lat1 = lat + random.randint(-1000, 1000) / 100000
        lon1 = lon + random.randint(-1000, 1000) / 100000
        brand = random.choice(bikeBrand)
        bike_data = Bikes(id, source, lat1, lon1, "Good", "Available", brand)
        db.session.add(bike_data)
        db.session.commit()
        bike = {
            "id": bike_data.id,
            "latitude": bike_data.latitude,
            "longitude": bike_data.longitude,
            "condition": bike_data.condition,
            "status": bike_data.status,
            "brand": bike_data.brand,
        }
        bikeInfo.append(bike);
    return bikeInfo


# get bikes from database based on users current locations(for test).
# parameter: source
# return: bike information list
def getBikesFromDatabase(source):
    bikeInfo = []
    rs = Bikes.query.filter(Bikes.source == source).all()
    for r in rs:
        bike = {
            "id": r.id,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "condition": r.condition,
            "status": r.status,
            "brand": r.brand,
        }
        bikeInfo.append(bike);
    print("info", bikeInfo)
    return bikeInfo


# generate random destination for bike route (for test)
@app.route("/getRandomDestination", methods = ['POST'])
def getRandomDestination():
    bikeId = request.form['bikeId']
    bikeInfo = Bikes.query.get(bikeId)
    oldLat = float(bikeInfo.latitude)
    oldLng = float(bikeInfo.longitude)
    print(oldLat, oldLng)
    latRadom = random.uniform(0.01, 0.03)
    lngRadom = random.uniform(0.01, 0.03)
    newlat = oldLat + (latRadom * random.choice((-1, 1)))
    newlng = oldLng + (lngRadom * random.choice((-1, 1)))
    print(newlat, newlng)
    return {"newlat": newlat, "newlng": newlng}


# update current bike location when rent finishes
@app.route("/updateBikeLocation", methods = ['POST'])
def updateBikeLocation():
    bikeId = request.form['bikeId']
    lat = request.form["lat"]
    lng = request.form["lng"]
    bikeInfo = Bikes.query.get(bikeId)
    bikeInfo.latitude = lat;
    bikeInfo.longitude = lng;
    db.session.commit()
    return bikeId

# get users' account balance
@app.route("/getBalance", methods = ["POST"])
def getBalance():
    userId = request.form['userid']
    # bikeId = request.form['rentBikeId']
    # bikeStatus = Bikes.query.get(bikeId).status
    userInfo = Customer.query.get(userId)
    bikeId = userInfo.bike_id
    return {"money": userInfo.money, "bikeId": bikeId}

# update users' account balance
@app.route("/updateBalance", methods = ["POST"])
def updateBalance():
    money = float(request.form['money'])
    userId = request.form['userid']
    userInfo = Customer.query.get(userId)
    userInfo.money = money
    db.session.commit()
    return userId

# rent function in customer page
@app.route("/rent", methods = ["POST"])
def rent():
    bikeId = request.form['bikeId']
    userId = request.form['userid']
    user_info = Customer.query.get(userId)
    user_info.bike_id = bikeId
    db.session.commit()
    bike_info = Bikes.query.get(bikeId)
    bike_info.status = "Unavailable"
    db.session.commit()
    return bikeId

# rent function in customer page
@app.route("/getBikeInitialLatAndLng", methods = ["POST"])
def getBikeInitialLatAndLng():
    bikeId = request.form['bikeId']
    bike_info = Bikes.query.get(bikeId)
    lat = bike_info.latitude
    lng = bike_info.longitude
    return {"lat": lat, "lng": lng}


# calculate function in customer page
@app.route("/calculate", methods = ["POST"])
def calculate():
    basic = 0.1
    time = request.form['time']
    print("time", time)
    minutes = math.ceil(int(time) / 60)
    userId = request.form['userid']
    distance = float(request.form['distance'])
    userInfo = Customer.query.get(userId)
    charge = minutes * basic
    balance = userInfo.money - charge
    userInfo.money = balance
    db.session.commit()
    bikeid = userInfo.bike_id
    bikeInfo = Bikes.query.get(bikeid)
    db.session.commit()
    bikeInfo.status = "Available"
    userInfo.bike_id = ""
    db.session.commit()
    rentID = random.randint(100000, 1000000)
    while RentRecords.query.get(rentID):
        rentID = random.randint(100000, 1000000)
    recordData = RentRecords(rentID, customerID = userId, bikeID = bikeid, ridingDuration = time, cost = charge,
                             distance = distance)
    db.session.add(recordData)
    db.session.commit()
    print(bikeid)
    return {"money": balance, "charge": charge, "bikeId": bikeid}

# report function in customer page
@app.route("/report", methods = ['POST'])
def report():
    bikeId = request.form['bikeId']
    print(bikeId)
    bikeInfo = Bikes.query.get(bikeId)
    bikeInfo.condition = 'Need Fixing'
    bikeInfo.status = "Unavailable"
    db.session.commit()
    return jsonify(bikeId)

# logout function in customer page
@app.route("/logout", methods = ['POST'])
def logout():
    userId = request.form['userid']
    print(userId)
    userInfo = Customer.query.get(userId)
    bikeId = userInfo.bike_id
    return {"bikeId": bikeId}

# check whether the bike is rent.
@app.route("/checkBikeIdValid", methods = ['POST'])
def checkBikeIdValid():
    bikeId = request.form['bikeId']
    bikeInfo = Bikes.query.get(bikeId)
    if not bikeInfo:
        return {"check": True}
    else:
        return {"check": False}

# check whether register info is valid
@app.route("/checkUserInfo", methods = ['POST'])
def checkUserInfo():
    username = request.form['username']
    password = request.form['password']
    userInfo = Customer.query.get(username)
    check = {
        "checkUsernameNotExist": False,
        "checkUsernameLength": False,
        "checkPasswordValid": False,
    }
    if not userInfo:
        check["checkUsernameNotExist"] = True
    if len(username) > 6:
        check["checkUsernameLength"] = True
    if len(password) > 6 and password.lower() != password:
        check["checkPasswordValid"] = True
    return check


# add some bikes for test
def generateRandomBikes2(lat, lon):
    for i in range(0, 50, 1):
        id = random.randint(1000000, 100000000)
        bike_info = Bikes.query.get(id)
        while bike_info:
            id = random.randint(1000000, 100000000)
            bike_info = Bikes.query.get(id)
        source = "{:.1f} {:.1f}".format(lat, lon)
        lat1 = lat + random.randint(-1000, 1000) / 100000
        lon1 = lon + random.randint(-1000, 1000) / 100000
        brand = random.choice(bikeBrand)
        condition = random.choice(["Good", "Need Fixing"])
        status = random.choice(["Available", "Unavailable"])
        bike_data = Bikes(id, source, lat1, lon1, condition, status, brand)
        db.session.add(bike_data)
        db.session.commit()

# generate random username for test
def generateUsername():
    username = ''
    for i in range(4):
        tmp = chr(random.randint(65, 90))
        username += str(tmp)
    for j in range(5):
        tmp = random.randint(0, 9)
        username += str(tmp)
    return username

# add some customers for test
def generateRandomUsers():
    for i in range(200):
        username = generateUsername()
        password = str(random.randint(1000000, 100000000)) + chr(random.randint(65, 90))
        user_data = Customer(username, password, 0)
        db.session.add(user_data)
        db.session.commit()

# add some rent records for test
def generateRandomRecords():
    customerIdList = [customer.id for customer in Customer.query.all()]
    bikeIdList = [bike.id for bike in Bikes.query.all()]

    print(customerIdList)
    print(bikeIdList)
    for i in range(500):
        customerId = random.choice(customerIdList)
        bikeId = random.choice(bikeIdList)
        rentId = random.randint(1000000, 10000000)
        while RentRecords.query.get(rentId):
            rentId = random.randint(100000, 1000000)
        time = random.randint(1, 1800)
        minutes = math.ceil(int(time) / 60)
        charge = (int(minutes * 0.1 * 10))/10
        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2021, 11, 1)
        distance = minutes * random.randint(3,6) * 60 / 1000
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)

        rentRecord = RentRecords(rentId, customerId, bikeId, time, charge, random_date, distance)
        db.session.add(rentRecord)
        db.session.commit()

# initial database (for test)
def init_database():
    # db.drop_all()
    db.create_all()
    # customer1 = Customer("lingrui", "123456", 0)
    # customer2 = Customer("xinyu", "123456", 0)
    # customer3 = Customer("peiyu", "123456", 0)
    # customer4 = Customer("lijia", "123456", 0)
    # customer5 = Customer("junfeng", "123456", 0)
    # customer6 = Customer("mickey", "123456", 0)
    # customer7 = Customer("ada1", "123456", 0)
    # db.session.add_all([customer1, customer2, customer3, customer4, customer5, customer6, customer7])
    # db.session.commit()
    #
    # # add some operators
    # operator1 = Operator("op1", "123123")
    # operator2 = Operator("op2", "123123")
    # operator3 = Operator("lingrui", "123123")
    # operator4 = Operator("xinyu", "123123")
    # operator5 = Operator("peiyu", "123123")
    # operator6 = Operator("lijia", "123123")
    # operator7 = Operator("junfeng", "123123")
    # operator8 = Operator("mickey", "123123")
    # operator9 = Operator("ada2", "123123")
    # db.session.add_all([operator1, operator2, operator3, operator4, operator5, operator6, operator7, operator8, operator9])
    # db.session.commit()
    #
    # # add some managers
    # manager1 = Manager("manager1", "987654321")
    # manager2 = Manager("manager2", "987654321")
    # manager3 = Manager("ada3", "987654321")
    # db.session.add_all([manager1, manager2, manager3])
    # db.session.commit()
    #
    # #random some bike
    # generateRandomBikes2(39.901911085388384, 116.37687195751951)  # beijing
    # generateRandomBikes2(31.401194668460988, 121.47793292999268)  # shanghai
    # generateRandomBikes2(22.271623458568882, 114.16211128234863)  # hongkong
    # generateRandomBikes2(34.72464836879197, 113.63489627838135)  # zhengzhou
    #
    # #random some customer
    # generateRandomUsers()
    #
    # #random some record
    # generateRandomRecords()


# initialize database
init_database()

if __name__ == '__main__':
    # app.run(host = "0.0.0.0", port = 8088, debug = True, ssl_context = 'adhoc')
    app.run(ssl_context = ('cert.pem','key.pem'))