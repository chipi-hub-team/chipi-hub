from flask import render_template, redirect, session, url_for, request, make_response
from flask_login import current_user, logout_user

from app.modules.auth import auth_bp
from app.modules.auth.forms import SignupForm, LoginForm, ValidateEmailForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService
import pyotp
import os

authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if not authentication_service.is_email_valid(email):
            return render_template("auth/signup_form.html", form=form, error=f'Email {email} in use')

        try:
            authentication_service.create_with_profile(**form.data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f'Error creating user: {exc}')

        response = make_response(redirect(url_for('auth.validate_email')))
        session['email'] = email
        session['password'] = password
        return response

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = request.form['email']
        password = request.form['password']
        if authentication_service.correct_credentials(email, password):
            response = make_response(redirect(url_for('auth.validate_email')))
            session['email'] = email
            session['password'] = password
            return response

        return render_template("auth/login_form.html", form=form, error='Invalid credentials')

    return render_template('auth/login_form.html', form=form)


@auth_bp.route('/validate_email', methods=['GET', 'POST'])
def validate_email():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    email = session['email']
    password = session['password']
    if not email or not password:
        return redirect(url_for('auth.login'))

    form = ValidateEmailForm()

    if request.method == 'POST':
        key = int(form.key.data.strip())
        if key == int(session.get('key')):
            authentication_service.login(email, password)
            response = make_response(redirect(url_for('public.index')))
            session.pop('email', None)
            session.pop('password', None)
            return response

        return render_template(
            "auth/validate_email_form.html",
            form=form,
            key=key,
            error='The key does not match'
        )

    if request.method == 'GET':
        random_key = pyotp.TOTP(str(os.getenv('SECRET_CODE_GENERATOR'))).now()
        session['key'] = random_key
        authentication_service.send_email(email, random_key)
    return render_template('auth/validate_email_form.html', form=form, email=email)


@auth_bp.route('/logout')
def logout():
    logout_user()
    response = make_response(redirect(url_for('public.index')))
    session.pop('email', None)
    session.pop('password', None)
    return response
