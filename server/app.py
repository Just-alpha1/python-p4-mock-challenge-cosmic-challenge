#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return [scientist.to_dict(rules=('-missions', '-planets')) for scientist in scientists]

    def post(self):
        data = request.get_json()
        try:
            scientist = Scientist(name=data['name'], field_of_study=data['field_of_study'])
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 201
        except ValueError as e:
            return {'errors': ['validation errors']}, 400
        except KeyError as e:
            return {'errors': ['validation errors']}, 400


class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        return scientist.to_dict()

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        data = request.get_json()
        try:
            if 'name' in data:
                scientist.name = data['name']
            if 'field_of_study' in data:
                scientist.field_of_study = data['field_of_study']
            db.session.commit()
            return scientist.to_dict(), 202
        except ValueError as e:
            return {'errors': ['validation errors']}, 400
        except KeyError as e:
            return {'errors': ['validation errors']}, 400

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {'error': 'Scientist not found'}, 404
        db.session.delete(scientist)
        db.session.commit()
        return '', 204


class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        return [planet.to_dict(rules=('-scientists', '-missions')) for planet in planets]


class Missions(Resource):
    def post(self):
        data = request.get_json()
        try:
            mission = Mission(
                name=data['name'],
                scientist_id=data['scientist_id'],
                planet_id=data['planet_id']
            )
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict(), 201
        except ValueError as e:
            return {'errors': ['validation errors']}, 400
        except KeyError as e:
            return {'errors': ['validation errors']}, 400


api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')


@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
