from flask_wtf import FlaskForm
from wtforms import SubmitField


class RatingForm(FlaskForm):
    submit = SubmitField('Save rating')
