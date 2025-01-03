import logging
import os
import json
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from zipfile import ZipFile

from flask import (
    redirect,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
    abort,
    url_for,
)
from flask_login import login_required, current_user

from app.modules.dataset.forms import DataSetForm
from app.modules.dataset.models import (
    DSDownloadRecord,
    Status
)
from app.modules.dataset import dataset_bp
from app.modules.dataset.services import (
    AuthorService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    DataSetService,
    DOIMappingService
)
from app.modules.rating.services import RatingService
from app.modules.zenodo.services import ZenodoService

logger = logging.getLogger(__name__)


dataset_service = DataSetService()
rating_service = RatingService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
zenodo_service = ZenodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()

    if request.method == "POST":

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:

            dataset = dataset_service.create_from_form(form=form, current_user=current_user)
            logger.info(f"Dataset created successfully: {dataset}")

            # Mover los modelos de características asociados
            dataset_service.move_feature_models(dataset)

            # Eliminar carpeta temporal del usuario
            file_path = current_user.temp_folder()
            if os.path.exists(file_path) and os.path.isdir(file_path):
                shutil.rmtree(file_path)

            return jsonify({"message": "Dataset created successfully!"}), 200

        except Exception as exc:
            return jsonify({"message": f"Error during dataset creation: {str(exc)}"}), 500

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():

    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
        status=Status,
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".uvl"):
        return jsonify({"message": "No valid file"}), 400

    # create temp folder
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, file.filename)

    if os.path.exists(file_path):
        # Generate unique filename (by recursion)
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(
            os.path.join(temp_folder, f"{base_name} ({i}){extension}")
        ):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "UVL uploaded and validated successfully",
                "filename": new_filename,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "Error: File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                relative_path = os.path.relpath(full_path, file_path)

                zipf.write(
                    full_path,
                    arcname=os.path.join(
                        os.path.basename(zip_path[:-4]), relative_path
                    ),
                )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(
            uuid.uuid4()
        )  # Generate a new unique identifier if it does not exist
        # Save the cookie to the user's browser
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


@dataset_bp.route("/dataset/download_all_datasets", methods=["GET"])
def download_all_datsets():
    datasets = dataset_service.get_all_datasets()

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "datasets.zip")

    with ZipFile(zip_path, "w") as zipf:
        for dataset in datasets:
            file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

            for subdir, dirs, files in os.walk(file_path):
                for file in files:
                    full_path = os.path.join(subdir, file)

                    relative_path = os.path.relpath(full_path, file_path)

                    zipf.write(
                        full_path,
                        arcname=os.path.join(
                            os.path.basename(zip_path[:-4]), relative_path
                        ),
                    )

    return send_from_directory(
        temp_dir,
        "datasets.zip",
        as_attachment=True,
        mimetype="application/zip",
    )


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):

    # Check if the DOI is an old DOI
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        # Redirect to the same path with the new DOI
        return redirect(url_for('dataset.subdomain_index', doi=new_doi), code=302)

    # Try to search the dataset by the provided DOI (which should already be the new one)
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    # Get dataset data
    dataset = ds_meta_data.data_set
    dataset_ratings = rating_service.get_total_ratings_for_dataset(dataset.id)
    user_already_rated = False
    if current_user.is_authenticated:
        user_already_rated = rating_service.user_already_rated_dataset(dataset.id, current_user.id)

    # Save the cookie to the user's browser
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(
        render_template(
            "dataset/view_dataset.html",
            dataset=dataset,
            current_user=current_user,
            dataset_ratings=dataset_ratings,
            user_already_rated=user_already_rated
        )
    )
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    if (dataset_service.get_by_id(dataset_id).user_id != current_user.id):
        abort(403)

    # Get dataset in case is from the current user
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    return render_template("dataset/view_dataset.html", dataset=dataset)


@dataset_bp.route("/dataset/publish", methods=["POST"])
@login_required
def publish_all_datasets():
    datasets = dataset_service.get_unsynchronized(current_user.id)
    errors = []

    for dataset in datasets:
        try:
            zenodo_response_json = zenodo_service.create_new_deposition(dataset)
            response_data = json.dumps(zenodo_response_json)
            data = json.loads(response_data)

            if not data.get("conceptrecid"):
                errors.append(f"Dataset ID {dataset.id}: Failed to create deposition on Zenodo.")
                continue

            deposition_id = data.get("id")

            try:
                dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

                for feature_model in dataset.feature_models:
                    try:
                        zenodo_service.upload_file(dataset, deposition_id, feature_model)
                    except Exception as e:
                        errors.append(f"Dataset ID {dataset.id}: Error uploading feature model. {str(e)}")

                zenodo_service.publish_deposition(deposition_id)
                deposition_doi = zenodo_service.get_doi(deposition_id)
                dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)

            except Exception as e:
                errors.append(f"Dataset ID {dataset.id}: Error during publication process. {str(e)}")

        except Exception as e:
            errors.append(f"Dataset ID {dataset.id}: Error creating dataset in Zenodo. {str(e)}")

    if errors:
        return jsonify({"message": "Publication completed with errors.", "errors": errors}), 207

    dataset_service.publish_datasets(current_user_id=current_user.id)
    return redirect("/dataset/list")


@dataset_bp.route("/dataset/<int:dataset_id>/publish", methods=["POST"])
@login_required
def publish_dataset(dataset_id):

    dataset = dataset_service.get_or_404(dataset_id)

    if dataset.ds_meta_data.ds_status == Status.PUBLISHED:
        return jsonify({"message": "Dataset is already published."}), 400

    dataset_service.publish_specific_dataset(current_user.id, dataset_id)

    try:
        zenodo_response_json = zenodo_service.create_new_deposition(dataset)
        data = json.loads(json.dumps(zenodo_response_json))

        if not data.get("conceptrecid"):
            return jsonify({"message": "Failed to create deposition on Zenodo."}), 400

        deposition_id = data.get("id")
        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

        for feature_model in dataset.feature_models:
            try:
                zenodo_service.upload_file(dataset, deposition_id, feature_model)
            except Exception as e:
                # Log the error instead of using continue
                logger.error(f"Error uploading feature model for dataset {dataset.id}: {str(e)}")

        zenodo_service.publish_deposition(deposition_id)
        deposition_doi = zenodo_service.get_doi(deposition_id)
        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)

        return redirect("/dataset/list")

    except Exception as exc:
        return jsonify({"message": f"Error during Zenodo publication process: {exc}"}), 500
