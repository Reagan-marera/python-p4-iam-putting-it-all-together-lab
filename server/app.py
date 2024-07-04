#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        user = json.get('username')
        password = json.get('password')
        image_url = json.get('image_url')
        bio = json.get('bio')
        new_user = User(
                username = user,
                image_url = image_url,
                bio = bio
            )
        new_user.password_hash = password
        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422
class CheckSession(Resource):
    def get(self):
            user = User.query.filter_by(id=session.get('user_id')).first()
            if user:
                return user.to_dict(), 200
            else:
                return {'message': '401: Not Authorized'}, 401
class Login(Resource):
    def post(self):
        json = request.get_json()
        username = json['username']
        password = json['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict()
        else:
            return {'message': '401: Not Authorized'}, 401
class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {'message': '204: No Content'}, 204
        return {'message': '401: Not Authorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            return [recipe.to_dict() for recipe in Recipe.query.all()]
        return {'message': '401: Not Authorized'}, 401

    def post(self):
        if not session.get('user_id'):
                    return {'message': '401: Not Authorized'}, 401
        if session.get('user_id'):
            json = request.get_json()
            title = json.get('title')
            instructions = json.get('instructions')
            minutes_to_complete = json.get('minutes_to_complete')
            try:
                new_recipe = Recipe(
                    title=title,
                    instructions=instructions,
                    minutes_to_complete=minutes_to_complete,
                    user_id = session['user_id'],
                )
                db.session.add(new_recipe)
                db.session.commit()
                
                return new_recipe.to_dict(), 201

            except IntegrityError:
                 return {'error': '422 Unprocessable Entity'}, 422
                
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)