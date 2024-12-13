from flask import jsonify, make_response
from app.modules.fakenodo import fakenodo_bp
import json
import uuid
import os


@fakenodo_bp.route('/fakenodo/deposit/depositions', methods=['GET'])
def get_all_depositions():
    workdir = os.getenv("WORKING_DIR")
    path = f"{workdir}app/modules/fakenodo/placeholders/deposition.json"
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:id>', methods=['GET'])
def get_deposition(id):
    workdir = os.getenv("WORKING_DIR")
    path = f"{workdir}/app/modules/fakenodo/placeholders/deposition.json"
    with open(path) as f:
        data = json.load(f)
        data['doi'] = str(uuid.uuid4())

    return jsonify(data)


@fakenodo_bp.route('/fakenodo/deposit/depositions', methods=['POST'])
def create_deposition():
    response = make_response(jsonify({"message": "Deposition created", "id": 1, "conceptrecid": "1234"}))
    response.status_code = 201
    return response


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:id>/files', methods=['POST'])
def upload_file(id):
    response = make_response(jsonify({"message": f"File uploaded to deposition {id}"}))
    response.status_code = 201
    return response


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:id>', methods=['DELETE'])
def delete_deposition(id):
    return jsonify({"message": f"Deposition {id} deleted"})


@fakenodo_bp.route('/fakenodo/deposit/depositions/<int:id>/actions/publish', methods=['POST'])
def publish_deposition(id):
    response = make_response(jsonify({"message": f"Deposition {id} published"}))
    response.status_code = 202
    return response
