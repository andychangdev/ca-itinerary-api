from datetime import date

from flask import Blueprint, request
from init import db
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.itinerary import Itinerary
from models.review import Review, review_schema, reviews_schema

reviews_bp = Blueprint("reviews", __name__, url_prefix="/<int:itinerary_id>/reviews")

# create a review
@reviews_bp.route("/", methods=["POST"])
@jwt_required()
def create_review(itinerary_id):
    data = request.get_json()
    stmt = db.select(Itinerary).filter_by(id=itinerary_id)
    itinerary = db.session.scalar(stmt)
    if itinerary:
        review = Review(
        rating = data.get("rating"),
        content = data.get("content"),
        date_posted = date.today(),
        user_id = get_jwt_identity(),
        itinerary_id = itinerary.id
        )
        db.session.add(review)
        db.session.commit()
        return review_schema.dump(review), 201
    else:
        return {"Error": f"Itinerary ID {itinerary_id} not found"}, 404
    

# retrieve reviews in an intinerary by rating
@reviews_bp.route("/rating/<int:review_rating>")
def retrieve_review_by_rating(itinerary_id, review_rating):
    stmt = db.select(Review).filter_by(rating=review_rating, itinerary_id=itinerary_id)
    reviews = db.session.scalars(stmt).all()
    if reviews:
        return reviews_schema.dump(reviews)
    else:
        return {"Error": f"No reviews with rating {review_rating} found in itinerary ID {itinerary_id}"}, 404
    

# delete an exisiting review
@reviews_bp.route("/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(itinerary_id, review_id):
    stmt = db.select(Review).filter_by(id=review_id)
    review = db.session.scalar(stmt)
    # if review exists and belongs in provided itinerary_id
    if review and review.itinerary.id == itinerary_id:
        user_id = get_jwt_identity()
        # if user_id matches the review's user_id
        if int(review.user.id) == int(user_id):
            db.session.delete(review)
            db.session.commit()
            return {"Success": f"Review ID {review_id} deleted successfully."}
        else:
            return {"Error": f"Unauthorized to delete Review ID {review_id} from Itinerary ID {itinerary_id}."}
    else:
        return {"Error": f"Review ID {review_id} not found in itinerary ID {itinerary_id}"}, 404
