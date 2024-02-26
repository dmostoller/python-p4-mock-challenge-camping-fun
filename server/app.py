#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, abort
from werkzeug.exceptions import NotFound
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


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        camper_list = [camper.to_dict(rules = ('-signups',)) for camper in Camper.query.all()]
        response = make_response(camper_list, 200)
        return response 
    
    def post(self):
        try:
            form_json = request.get_json()
            new_camper = Camper(
                name=form_json["name"],
                age=form_json["age"],
            )
            db.session.add(new_camper)
            db.session.commit() 
            response = make_response(new_camper.to_dict(rules = ('-signups', )), 201)
        except ValueError:
            response = make_response({"errors" : ["validation errors"]}, 400)

        return response

class CampersById(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            response = make_response(camper.to_dict(), 200)
        else:    
            response = make_response({"error" : "Camper not found"}, 404)
        return response 

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            try:                
                for attr in request.get_json():
                    setattr(camper, attr, request.get_json()[attr])
                db.session.add(camper)
                db.session.commit()    
                response = make_response(camper.to_dict(rules = ('-signups', )), 202)
            except ValueError:
                response = make_response({"errors" : ["validation errors"]}, 400)
        else:
            response = make_response({"error" : "Camper not found"}, 404)


        return response 


class Activities(Resource):
    def get(self):
        activities_list = [activity.to_dict(rules = ("-signups", )) for activity in Activity.query.all()]
        return make_response(activities_list, 200)
    
class ActivitiesById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            response = make_response({}, 204)
        else:
            response = make_response({"error" : "Activity not found"}, 404)
        return response

class Signups(Resource):
    def post(self):
        form_json = request.get_json()
        try: 
            new_signup = Signup(
                camper_id=form_json["camper_id"],
                activity_id=form_json["activity_id"],
                time=form_json["time"]
            )
            db.session.add(new_signup)
            db.session.commit()
            response = make_response(new_signup.to_dict(), 201)
        except ValueError:
            response = make_response({"errors" : ["validation errors"]}, 400)

        return response 

api.add_resource(Campers, "/campers")
api.add_resource(CampersById, "/campers/<int:id>")
api.add_resource(Activities, "/activities")
api.add_resource(ActivitiesById, "/activities/<int:id>")
api.add_resource(Signups, "/signups")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
