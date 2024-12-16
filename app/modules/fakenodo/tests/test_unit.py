import pytest
from unittest.mock import patch, MagicMock
from app.modules.fakenodo.services import FakenodoService
from app.modules.fakenodo.routes import (
    get_all_depositions,
    get_deposition,
    create_deposition,
    upload_file,
    delete_deposition,
    publish_deposition
)


@pytest.fixture
def fakenodo_service():
    return FakenodoService()


def test_get_all_depositions(fakenodo_service):
    with patch('app.modules.fakenodo.routes.os.getenv', return_value='/fake/path/'), \
         patch('app.modules.fakenodo.routes.open', MagicMock(
             return_value=MagicMock(
                 __enter__=lambda s: s,
                 __exit__=lambda s, t, v, tb: None,
                 read=lambda: '{"data": "fake"}'
             )
         )):

        response = get_all_depositions()
        assert response.status_code == 200
        assert response.json == {"data": "fake"}


def test_get_deposition(fakenodo_service):
    with patch('app.modules.fakenodo.routes.os.getenv', return_value='/fake/path/'), \
         patch('app.modules.fakenodo.routes.open', MagicMock(
             return_value=MagicMock(
                 __enter__=lambda s: s,
                 __exit__=lambda s, t, v, tb: None,
                 read=lambda: '{"data": "fake"}'
             )
         )), \
            patch('app.modules.fakenodo.routes.uuid.uuid4', return_value='fake-uuid'):

        response = get_deposition(1)
        assert response.status_code == 200
        assert response.json == {"data": "fake", "doi": "fake-uuid"}


def test_create_deposition(fakenodo_service):
    response = create_deposition()
    assert response.status_code == 201
    assert response.json == {"message": "Deposition created", "id": 1, "conceptrecid": "1234"}


def test_upload_file(fakenodo_service):
    response = upload_file(1)
    assert response.status_code == 201
    assert response.json == {"message": "File uploaded to deposition 1"}


def test_delete_deposition(fakenodo_service):
    response = delete_deposition(1)
    assert response.status_code == 200
    assert response.json == {"message": "Deposition 1 deleted"}


def test_publish_deposition(fakenodo_service):
    response = publish_deposition(1)
    assert response.status_code == 202
    assert response.json == {"message": "Deposition 1 published"}
