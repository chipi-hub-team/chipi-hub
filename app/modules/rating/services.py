from app.modules.rating.repositories import RatingRepository
from core.services.BaseService import BaseService
from app.modules.rating.models import Rating


class RatingService(BaseService):
    def __init__(self):
        super().__init__(RatingRepository())

    def add_or_remove_rating(self, dataset_id, user_id, model_id=None):
        rating = Rating(dataset_id=dataset_id, user_id=user_id, model_id=model_id)
        if (model_id and not self.user_already_rated_model(model_id, user_id)) or (not model_id and not self.user_already_rated_dataset(dataset_id, user_id)):
            self.repository.add(rating)
            self.repository.commit()
        else:
            self.remove_ratings(dataset_id, user_id, model_id)

    def remove_ratings(self, dataset_id, user_id, model_id):
        if model_id:
            ratings = self.repository.get_by_model_id_and_user_id(model_id, user_id)
        else:
            ratings = self.repository.get_by_dataset_id_and_user_id(dataset_id,user_id)
        if ratings:
            for rating in ratings:
                self.repository.delete(rating)
            self.repository.commit()


    def user_already_rated_dataset(self, dataset_id, user_id):
        if self.repository.get_by_dataset_id_and_user_id(dataset_id, user_id):
            return True
        return False

    def user_already_rated_model(self, model_id, user_id):
        if self.repository.get_query().filter_by(model_id=model_id, user_id=user_id).first():
            return True
        return False

    def get_total_ratings_for_dataset(self, dataset_id):
        return self.repository.get_query().filter_by(dataset_id=dataset_id, model_id=None).count()

    def get_total_ratings_for_model(self, model_id):
        return self.repository.get_query().filter_by(model_id=model_id).count()
