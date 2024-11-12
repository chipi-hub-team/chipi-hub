import pytest


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


def test_download_all_dataset(test_client):
    response = test_client.get(
        "/dataset/download_all_datasets", follow_redirects=True
    )

    assert response.status_code == 200, "Download all datasets was unsuccessful"

    test_client.get("/logout", follow_redirects=True)
