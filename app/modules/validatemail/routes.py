from flask import flash, redirect, render_template, url_for
from flask_login import login_user
from app.modules.validatemail import validatemail_bp
from app.modules.validatemail.services import ValidatemailService

validatemail_service = ValidatemailService()


@validatemail_bp.route('/validatemail', methods=['GET'])
def index():
    return render_template('validatemail/index.html')


@validatemail_bp.route("/validate_user/<token>", methods=["GET"])
def validate_user(token):
    try:
        user = validatemail_service.validate_user_with_token(token)
    except Exception as exc:
        flash(exc.args[0], "danger")
        return redirect(url_for("auth.show_signup_form"))

    # Log user
    login_user(user, remember=True)
    return redirect(url_for("public.index"))