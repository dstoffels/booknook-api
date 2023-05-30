from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_restful import Resource
from database.models import db, Review, Favorite
from database.schemas import review_schema, reviews_schema, favorite_schema, favorites_schema
from marshmallow import ValidationError


class UserReviewsResource(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            new_review = review_schema.load(data)
            new_review.user_id = user_id
            db.session.add(new_review)
            db.session.commit()
            return review_schema.dump(new_review), 201
        except ValidationError as e:
            return {"messages": e.messages}, 400


class UserFavoritesResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        new_fav = favorite_schema.load(data)
        new_fav.user_id = user_id
        db.session.add(new_fav)
        db.session.commit()
        return favorite_schema.dump(new_fav), 201

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user_favs = Favorite.query.filter_by(user_id=user_id)
        return favorites_schema.dump(user_favs), 200


class BookInfoResource(Resource):
    @jwt_required()
    def get(self, book_id):
        book_reviews = Review.query.filter_by(book_id=book_id)
        book_reviews = reviews_schema.dump(book_reviews)

        avg_rating = 0
        for review in book_reviews:
            avg_rating += review["rating"] / len(book_reviews)

        user_id = get_jwt_identity()
        fav = Favorite.query.filter_by(book_id=book_id, user_id=user_id).first()

        return {
            "reviews": book_reviews,
            "average_rating": round(avg_rating, 1),
            "is_user_favorite": bool(fav),
        }, 200
