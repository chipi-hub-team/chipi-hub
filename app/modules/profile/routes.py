from app.modules.auth.models import User
from app.modules.auth.services import AuthenticationService
from app.modules.dataset.models import DataSet
from flask import abort, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from app import db
from app.modules.profile import profile_bp
from app.modules.profile.forms import UserProfileForm
from app.modules.profile.services import UserProfileService


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    auth_service = AuthenticationService()
    profile = auth_service.get_authenticated_user_profile
    if not profile:
        return redirect(url_for("public.index"))

    form = UserProfileForm()
    if request.method == "POST":
        service = UserProfileService()
        result, errors = service.update_profile(profile.id, form)
        return service.handle_service_response(
            result, errors, "profile.edit_profile", "Profile updated successfully", "profile/edit.html", form
        )

    return render_template("profile/edit.html", form=form)


@profile_bp.route('/profile/summary', defaults={'user_id': None})
@profile_bp.route('/profile/summary/<int:user_id>')
@login_required
def my_profile(user_id):
    is_my_profile = False
    # ver si el user_id es none(mi perfil) o es alguno(perfil de otro)
    if user_id is None:
        user_id = current_user.id
        is_my_profile = True

    page = request.args.get('page', 1, type=int)
    per_page = 5

    # se busca el perfil del usuario del id de la url par mostrarlo dsps
    user_found = db.session.query(User).filter(User.id == user_id).first()

    if not user_found:
        abort(404)

    user_datasets_pagination = db.session.query(DataSet) \
        .filter(DataSet.user_id == user_id) \
        .order_by(DataSet.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    total_datasets_count = db.session.query(DataSet) \
        .filter(DataSet.user_id == user_id) \
        .count()

    print(user_datasets_pagination.items)

    return render_template(
        'profile/summary.html',
        user_profile=user_found.profile,
        user=user_found,
        datasets=user_datasets_pagination.items,
        pagination=user_datasets_pagination,
        total_datasets=total_datasets_count,
        is_my_profile=is_my_profile
    )
