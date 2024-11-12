from flask_wtf import FlaskForm
from wtforms import SubmitField


class ValidateMailForm(FlaskForm):
    submit = SubmitField('Save validatemail')