import pytest
from unittest.mock import patch, MagicMock
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.dataset.models import Status
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


@pytest.mark.local
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


@pytest.mark.local
def test_publish_all_datasets_success(test_client):
    """
    Positive case: Publish all unpublished datasets.
    """
    login_response = login(test_client, "testuser@example.com", "1234")
    assert login_response.status_code == 200, "Login was failed."

    with patch("app.modules.dataset.services.DataSetService.get_unsynchronized") as mock_get_datasets, \
         patch("app.modules.zenodo.services.ZenodoService.create_new_deposition") as mock_zenodo, \
         patch("app.modules.zenodo.services.ZenodoService.upload_file") as mock_upload_file:

        mock_upload_file.return_value = None
        mock_get_datasets.return_value = [
            MagicMock(
                id=500,
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
            ),
            MagicMock(
                id=501,
                ds_meta_data_id=1001,
                ds_meta_data=MagicMock(
                    ds_status="unpublished",
                    title="Dataset 2",
                    description="Description of dataset 2",
                    publication_type="DATA_MANAGEMENT_PLAN",
                    dataset_doi=None,
                ),
                feature_models=[
                    MagicMock(id=103, name="FeatureModel3"),
                ],
            ),
        ]

        mock_zenodo.return_value = {"conceptrecid": "12345", "id": "67890"}

        print("Mocked datasets:", mock_get_datasets.return_value)
        print("Mocked Zenodo response:", mock_zenodo.return_value)
        response = test_client.post("/dataset/publish", follow_redirects=True)
        print("Response", response.get_json())
        assert response.status_code == 200, "Publishing all unpublished datasets failed."
        mock_get_datasets.assert_called()

    logout(test_client)


def test_publish_dataset_already_published(test_client):
    """
    Negative case: Try to publish an already published dataset.
    """
    dataset_id = 1
    login_response = login(test_client, "testuser@example.com", "1234")
    assert login_response.status_code == 200, "Login was failed."

    with patch("app.modules.dataset.services.DataSetService.get_or_404") as mock_get_dataset:
        mock_get_dataset.return_value = MagicMock(ds_meta_data=MagicMock(ds_status=Status.PUBLISHED))

        response = test_client.post(f"/dataset/{dataset_id}/publish", follow_redirects=True)
        assert response.status_code == 400, "It should not allow publishing an already published dataset."
        assert response.json["message"] == "Dataset is already published."

    logout(test_client)


def test_publish_all_datasets_with_errors(test_client):
    """
    Negative case: Publish all unpublished datasets with some errors
    """
    login_response = login(test_client, "testuser@example.com", "1234")
    assert login_response.status_code == 200, "Login fue fallido."

    with patch("app.modules.dataset.services.DataSetService.get_unsynchronized") as mock_get_datasets, \
         patch("app.modules.zenodo.services.ZenodoService.create_new_deposition") as mock_zenodo:
        mock_get_datasets.return_value = [MagicMock(id=2), MagicMock(id=3)]
        mock_zenodo.side_effect = Exception("Error creating deposition")

        response = test_client.post("/dataset/publish", follow_redirects=True)
        assert response.status_code == 207, "The errored publication did not return the expected status."
        assert "Publication completed with errors." in response.json["message"]

    logout(test_client)
