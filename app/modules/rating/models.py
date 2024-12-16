from app import db


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Rating<{self.id}, Dataset<{self.dataset_id}>, User<{self.user_id}>>'
