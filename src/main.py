"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)



""" User methods """


@app.route('/user', methods=['POST'])
def User_add():
    request_body_user = request.get_json()

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    email = request.json.get('email', None)

    if username is None:
        return 'You need to specify the username', 400
    if password is None:
        return 'You need to specify the password', 400
    if email is None:
        return 'You need to specify the email', 400

    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify({"msg": "User already exists"})
    else:
        new_user = User(username=request_body_user["username"],
                        email=request_body_user["email"], 
                        password=request_body_user["password"])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User added successfully!"}), 200



@app.route("/user", methods=["GET"])
def User_get():
    user = User.query.all()
    user = list(map(lambda user: user.serialize(), user))
    return jsonify({"results": user})



@app.route("/user/<int:id>", methods=["GET"])
def User_get_id(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({
            "Error": "User not found"
        }), 404

    return jsonify(user.serialize()), 200



@app.route("/user/<int:id>/favorito", methods=["GET"])
def User_favoritos(id):
    favoritos = User.query.get(id)
    if favoritos is None:
        return jsonify({
            "Error": "No hay favoritos"
        }), 404

    return jsonify(favoritos.serialize_with_favs()), 200



""" Favoritos methods """


@app.route('/user/<int:id>/favorito/', methods=['POST'])
def favorito_add(id):
    request_body = request.get_json()

    type_add = request.json.get('type_add', None)

    if type_add == "character":

        name = request.json.get('name', None)
        description = request.json.get('description', None)
        birth_year = request.json.get('birth year', None)
        gender = request.json.get('gender', None)

        if name is None:
            return 'You need to specify the name', 400
        if description is None:
            return 'You need to specify the description', 400
        if birth_year is None:
            return 'You need to specify the birth year', 400
        if gender is None:
            return 'You need to specify the gender', 400

        user_info = User.query.get(id)
        list_favorito = [char['name'] for char in user_info.get_fav_character()]

        if name in list_favorito:
            return jsonify({
                "Message": "This character already exists in the favourite list"
            })

        else:
            new_fav_character = Character(name=request_body["name"],
                                      description=request_body["description"],
                                      birth_year=request_body["birth year"],
                                      gender=request_body["gender"],
                                      user_id=id)
            db.session.add(new_fav_character)
            db.session.commit()
            return jsonify({
                "Message": "Favorito added successfully!"
            })

    elif type_add == "planet":
        name = request.json.get('name', None)
        description = request.json.get('description', None)
        population  = request.json.get('population', None)
        climate  = request.json.get('climate', None)

        if name is None:
            return 'You need to specify the name', 400
        if description is None:
            return 'You need to specify the description', 400
        if population is None:
            return 'You need to specify the population', 400
        if climate is None:
            return 'You need to specify the climate', 400

        user_info = User.query.get(id)
        list_favorito = [plan['name'] for plan in user_info.get_fav_planet()]

        if name in list_favorito:
            return jsonify({
                "Message": "This planet already exists in the favourite list"
            })

        else:
            new_fav_planet = Planet(name=request_body["name"],
                        description=request_body["description"], 
                        population=request_body["population"],
                        climate=request_body["climate"],
                        user_id=id)
            db.session.add(new_fav_planet)
            db.session.commit()
            return jsonify({
                "Message": "Favorito added successfully!"
            })
    else:
        return jsonify({
            "Error": "Unavailable type to add, insert 'planet' or 'character'"
        })



""" Delete methods """


@app.route('/favorito/<int:id>', methods=['DELETE'])
def delete_favorito(id):
    request_body = request.get_json()
    user_info = User.query.get(id)
    type_delete = request.json.get("type_delete", None)

    if type_delete == "character":
        character_id = request.json.get("character_id", None)
        list_idFavorito = [char['id'] for char in user_info.get_fav_character()]

        if character_id in list_idFavorito:
            character_delete = Character.query.get(character_id)
            db.session.delete(character_delete)
            db.session.commit()
            return jsonify({
                "Message": "Character favourite successfully deleted"
            })
        else:
            return jsonify({
                "Error": "The character doesn't exist in the favourite list"
            })

    elif type_delete == "planet":
        planet_id = request.json.get("planet_id", None)
        list_idFavorito = [plan['id'] for plan in user_info.get_fav_planet()]

        if planet_id in list_idFavorito:
            planet_delete = Planet.query.get(planet_id)
            db.session.delete(planet_delete)
            db.session.commit()
            return jsonify({
                "Message": "Planet favourite successfully deleted"
            })
        else:
            return jsonify({
                "Error": "The planet doesn't exist in the favourite list"
            })
    else:
        return jsonify({
            "Error": "Unavailable type to delete, insert 'planet' or 'character'"
        })



""" Characters methods """


@app.route('/character', methods=['POST'])
def Character_add():
    request_body_character = request.get_json()

    name = request.json.get('name', None)
    description = request.json.get('description', None)
    birth_year = request.json.get('birth year', None)
    gender = request.json.get('gender', None)
    user_id = request.json.get('user_id', None)

    if name is None:
        return 'You need to specify the name', 400
    if description is None:
        return 'You need to specify the description', 400
    if birth_year is None:
        return 'You need to specify the birth year', 400
    if gender is None:
        return 'You need to specify the gender', 400
    if user_id is None:
        return 'You need to specify the user id', 400

    character = Character.query.filter_by(name=name).first()

    if character:
        return jsonify({"msg": "Character already exists"})
    else:
        new_character = Character(name=request_body_character["name"],
                                  description=request_body_character["description"],
                                  birth_year=request_body_character["birth year"],
                                  gender=request_body_character["gender"],
                                  user_id=request_body_character['user_id'])
        db.session.add(new_character)
        db.session.commit()
        return jsonify({"msg": "Character added successfully!"}), 200



@app.route("/character", methods=["GET"])
def Character_get():
    character = Character.query.all()
    character = list(map(lambda character: character.serialize(), character))
    return jsonify({"results": character})



@app.route("/character/<int:id>", methods=["GET"])
def Character_get_id(id):
    character = Character.query.get(id)
    if character is None:
        return jsonify({
            "Error": "Character not found"
        }), 404

    return jsonify(character.serialize()), 200



""" Planets methods """


@app.route('/planet', methods=['POST'])
def Planet_add():
    request_body_planet = request.get_json()

    name = request.json.get('name', None)
    description = request.json.get('description', None)
    population  = request.json.get('population', None)
    climate  = request.json.get('climate', None)
    user_id = request.json.get('user_id', None)

    if name is None:
        return 'You need to specify the name', 400
    if description is None:
        return 'You need to specify the description', 400
    if population is None:
        return 'You need to specify the population', 400
    if climate is None:
        return 'You need to specify the climate', 400
    if user_id is None:
        return 'You need to specify the user id', 400

    planet = Planet.query.filter_by(name=name).first()

    if planet:
        return jsonify({"msg": "Planet already exists"})
    else:
        new_planet = Planet(name=request_body_planet["name"],
                        description=request_body_planet["description"], 
                        population=request_body_planet["population"],
                        climate=request_body_planet["climate"],
                        user_id=request_body_planet['user_id'])
        db.session.add(new_planet)
        db.session.commit()
        return jsonify({"msg": "Planet added successfully!"}), 200



@app.route("/planet", methods=["GET"])
def Planet_get():
    planet = Planet.query.all()
    planet = list(map(lambda planet: planet.serialize(), planet))
    return jsonify({"results": planet})



@app.route("/planet/<int:id>", methods=["GET"])
def Planet_get_id(id):
    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({
            "Error": "Planet not found"
        }), 404

    return jsonify(planet.serialize()), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
