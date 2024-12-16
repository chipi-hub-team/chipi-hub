from app.modules.rating.models import Rating
from core.repositories.BaseRepository import BaseRepository


class RatingRepository(BaseRepository):
    def __init__(self):
        super().__init__(Rating)

    def add(self, rating):
        self.session.add(rating)

    def delete(self, rating):
        self.session.delete(rating)

    def get_by_id(self, rating_id):
        return self.session.query(Rating).filter_by(id=rating_id).first()

    def get_by_dataset_id(self, dataset_id):
        return self.session.query(Rating).filter_by(dataset_id=dataset_id).all()

    def get_by_dataset_id_and_user_id(self, dataset_id, user_id):
        return self.session.query(Rating).filter_by(dataset_id=dataset_id, user_id=user_id).all()

    def commit(self):
        self.session.commit()

    def get_query(self):
        return self.session.query(Rating)

    def query(self):
        return self.get_query()
