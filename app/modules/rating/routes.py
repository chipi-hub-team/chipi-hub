from flask import render_template, request, jsonify
from app.modules.rating import rating_bp
from app.modules.rating.services import RatingService
from flask_login import current_user

rating_service = RatingService()

@rating_bp.route('/rating', methods=['GET'])
def index():
    return render_template('rating/index.html')

@rating_bp.route('/rating/add', methods=['POST'])
def add_rating():
    data = request.get_json()
    dataset_id = data.get('dataset_id')
    user_id = data.get('user_id')
    model_id = data.get('model_id', None)
    
    rating_service.add_or_remove_rating(dataset_id, user_id, model_id)
    return jsonify({'message': 'Rating added successfully'}), 201

@rating_bp.route('/rating/remove/<int:rating_id>', methods=['DELETE'])
def remove_rating(rating_id):
    rating_service.remove_rating(rating_id)
    return jsonify({'message': 'Rating removed successfully'}), 200

@rating_bp.route('/rating/total/dataset/<int:dataset_id>', methods=['GET'])
def total_ratings_for_dataset(dataset_id):
    total = rating_service.get_total_ratings_for_dataset(dataset_id)
    user_already_rated = rating_service.user_already_rated_dataset(dataset_id, current_user.id)
    return jsonify({'total_ratings': total, 'user_already_rated': user_already_rated}), 200

@rating_bp.route('/rating/total/model/<int:model_id>', methods=['GET'])
def total_ratings_for_model(model_id):
    total = rating_service.get_total_ratings_for_model(model_id)
    return jsonify({'total_ratings': total}), 200
