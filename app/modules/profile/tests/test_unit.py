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
    Se testeará que el usuario pueda acceder al perfil de uno de los
    usuarios exsistentes mediante GET
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/summary/2")
    assert response.status_code == 200, "The profile page could not be accessed."
    assert b"User profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_get_unexisting_profile_page(test_client):
    """
    Se testeará que el usuario pueda acceder al perfil de uno de los
    usuarios exsistentes mediante GET
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/summary/12")
    assert response.status_code == 404, "The profile page could not be accessed."

    logout(test_client)


def test_get_my_profile_page(test_client):
    """
    Se testeará que el usuario pueda acceder al perfil de uno de los
    usuarios exsistentes mediante GET
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/summary")
    assert response.status_code == 200, "The profile page could not be accessed."
    assert b"My profile" in response.data, "The expected content is not present on the page"

    logout(test_client)
