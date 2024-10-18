import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_list_empty_notepad_get(test_client):
    """
    Tests access to the empty notepad list via GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/notepad")
    assert response.status_code == 200, "The notepad page could not be accessed."
    assert b"You have no notepads." in response.data, "The expected content is not present on the page"

    logout(test_client)

def test_get_one_notepad_get(test_client):
    """
    Tests access to a notepad via GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    test_client.post("/notepad/create", json={'title':'Titulo', 'body':'Cuerpo'}, follow_redirects=True)

    response = test_client.get("/notepad/1")
    assert response.status_code == 200, "The notepad page could not be accessed."

    logout(test_client)

def test_get_notepad_not_found(test_client):
    """
    Tests access to a notepad that does not exist via GET request.
    """

    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/notepad/7")
    assert response.status_code == 404, "The notepad page could not be accessed."

    logout(test_client)

def test_create_notepad_post(test_client):
    """
    Test create a new task via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post("/notepad/create", json={'title':'Titulo', 'body':'Cuerpo'}, follow_redirects=True)
    assert b"Titulo" in response.data, "The expected content is not present on the page"

    logout(test_client)

def test_edit_notepad_get(test_client):
    """
    Tests access to the notepad editing page via GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    create_response = test_client.post("/notepad/create", json={'title':'Titulo', 'body':'Cuerpo'}, follow_redirects=True)

    # Get id
    id = create_response.data.decode('utf-8').split('notepad/edit/')[1].split('"')[0]

    edit_response = test_client.get(f"/notepad/edit/{id}")
    assert edit_response.status_code == 200, "The notepad editing page could not be accessed."
    assert b"Save notepad" in edit_response.data, "The expected content is not present on the page"

    logout(test_client)

def test_edit_notepad_post(test_client):
    """
    Test edit a notepad via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    create_response = test_client.post("/notepad/create", json={'title':'Titulo', 'body':'Cuerpo'}, follow_redirects=True)

    # Get id
    id = create_response.data.decode('utf-8').split('notepad/edit/')[1].split('"')[0]

    edit_response = test_client.post(f"/notepad/edit/{id}", json={'title':'Titulo', 'body':'Cuerpo'}, follow_redirects=True)
    assert b"Titulo" in edit_response.data, "The expected content is not present on the page"

    logout(test_client)

def test_delete_notepad_post(test_client):
    """
    Test delete a notepad via POST request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    create_response = test_client.post("/notepad/create", json={'title':'Titulo', 'body':'Cuerpo'}, follow_redirects=True)

    # Get id
    id = create_response.data.decode('utf-8').split('notepad/edit/')[1].split('"')[0]

    delete_response = test_client.post(f"/notepad/delete/{id}")

    assert delete_response.status_code == 302, "The notepad could not be deleted."

    logout(test_client)

                           
