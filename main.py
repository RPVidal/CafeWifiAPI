from flask import Flask, jsonify, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from random import randint, choice
import os

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self) -> dict:
        """Returns a query row as a dictionary"""
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


# HTTP GET - Read Record
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def get_random_caffe():
    # returns the number of rows fo the table Cafe
    # table_len = Cafe.query.count()
    # random_cafe = Cafe.query.get(randint(1, table_len))

    # instead of generating a random number and then query the database by id i will just use
    # a more straightforward  method below - New method below

    # gets all the rows from our database
    cafes = db.session.query(Cafe).all()
    # choooses a random row
    random_cafe = choice(cafes)
    # first converts our row to a dictionary and then returns it as a json response in the browser
    return jsonify(random_cafe.to_dict())



@app.route("/all")
def all_cafes():
    """Returns all the entries in the database and returns a flask response type of object """
    return jsonify([item.to_dict() for item in db.session.query(Cafe).all()])


@app.route("/search")
def search_cafe():
    query_location = request.args.get("location")
    cafes = db.session.query(Cafe).filter(Cafe.location == query_location).all()
    # cafes_nearby = Cafe.query.filter(Cafe.location == location)

    if cafes:
        return jsonify([item.to_dict() for item in cafes])
    else:
        return jsonify(error={"Not found": "We don't know a cafe in that particular location"})


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    try:
        new_cafe = Cafe(name=request.args.get("name"), map_url=request.args.get("map_url"), img_url=request.args.get("img_url"),
                            location=request.args.get("location"), has_sockets=request.args.get("has_sockets"),
                            has_toilet=request.args.get("has_toilet"), has_wifi=request.args.get("has_wifi"),
                            can_take_calls=request.args.get("can_take_calls"), seats=request.args.get("seats"),
                            coffee_price=request.args.get("coffee_price"))
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(success={"Successfully added": "A new cafe has been added to our database"})
    except:
        return jsonify(error={"Error": "We couldn't add a new cafe due to invalid or missing information about the cafe, "
                                       "please input valid information about a cafe"})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_price(cafe_id):
    try:
        cafe_to_update = db.session.query(Cafe).filter(Cafe.id == int(cafe_id)).first()
        new_price = float(request.args.get("coffee_price"))
        cafe_to_update.coffee_price = "£" + str(new_price)
        db.session.commit()
        return jsonify(response={"Success":  "successfully updated the price"}), 200
    except:
        return jsonify(response={"Error": "The information you provided is invalid therefore we couldn't update "
                                          "the coffee price."
                                       " Please input valid information!"}), 404


# HTTP DELETE - Delete Records
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("TopSecretAPIKey")
    cafe_to_delete = db.session.query(Cafe).filter(Cafe.id == cafe_id).first()

    if cafe_to_delete and api_key == "FUCK_YOU":
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(response={"Success": "The cafe has been successfully deleted"}), 200
    else:
        return jsonify(response={"Error": "either you don't have permission to delete a record or the id you entered has not been found i our database"}), 403


if __name__ == '__main__':
    app.run(debug=True,)
