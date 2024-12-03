from app import db


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, nullable=False)
    model_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Rating<{self.id}, Dataset<{self.dataset_id}>, Model<{self.model_id}>, User<{self.user_id}>>'
