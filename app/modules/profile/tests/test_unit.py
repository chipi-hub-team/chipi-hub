import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_edit_profile_page_get(test_client):
    """
    Tests access to the profile editing page via a GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."
    assert b"Edit profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_get_profile_page(test_client):

    """
    Will test that an user will be able to access to another user's profile using GET
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/summary/2")
    assert response.status_code == 200, "The profile page could not be accessed."

    logout(test_client)


def test_get_unexisting_profile_page(test_client):
    """
    Will test that a user wont be able to access a profile of a non existent user
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/summary/12")
    assert response.status_code == 404, "The profile page could not be accessed."

    logout(test_client)


def test_get_my_profile_page(test_client):
    """
    Will test that the current user will be able to access it's profile using GET
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/summary")
    assert response.status_code == 200, "The profile page could not be accessed."
    assert b"My profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_get_my_profile_page_alternative_version(test_client):
    """
    Will test that the current user will be able to access it's profile using GET
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Obtenemos el ID del usuario logueado desde la base de datos
    user = User.query.filter_by(email='user@example.com').first()
    assert user is not None, "User not found in the database."

    # Realizamos la solicitud GET con el ID del usuario en la URL
    response = test_client.get(f"/profile/summary/{user.id}")
    assert response.status_code == 200, "The profile page could not be accessed."
    assert b"My profile" in response.data, "The expected content is not present on the page"

    logout(test_client)
