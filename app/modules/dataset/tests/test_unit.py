import pytest
from unittest.mock import patch, MagicMock
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app import db


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        # Create a test user
        user_test = User(email="testuser@example.com", password="1234")
        db.session.add(user_test)
        db.session.commit()

    yield test_client


def test_download_all_dataset(test_client):
    response = test_client.get(
        "/dataset/download_all_datasets", follow_redirects=True
    )

    assert response.status_code == 200, "Download all datasets was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_publish_dataset_success(test_client):
    """
    Positive case: Publish an unpublished dataset.
    """
    dataset_id = 500
    login_response = login(test_client, "testuser@example.com", "1234")
    assert login_response.status_code == 200, "Login was failed."

    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get_dataset, \
         patch("app.modules.zenodo.services.ZenodoService.create_new_deposition") as mock_zenodo, \
         patch("app.modules.zenodo.services.ZenodoService.upload_file") as mock_upload_file:

        mock_get_dataset.return_value = MagicMock(
            id=dataset_id,
            ds_meta_data_id=1000,
            ds_meta_data=MagicMock(
                ds_status="unpublished",
                title="Dataset 1",
                description="Description of dataset 1",
                publication_type="DATA_MANAGEMENT_PLAN",
                dataset_doi=None,
            ),
            feature_models=[
                MagicMock(id=101, name="FeatureModel1"),
                MagicMock(id=102, name="FeatureModel2"),
            ],
        )

        mock_upload_file.return_value = None
        mock_zenodo.return_value = {"conceptrecid": "12345", "id": "67890"}

        response = test_client.post(f"/dataset/{dataset_id}/publish", follow_redirects=True)
        print("Response", response.get_json())
        assert response.status_code == 200, "Publishing the unpublished dataset failed."
        mock_get_dataset.assert_called_once_with(dataset_id)

    logout(test_client)
