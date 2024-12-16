import pytest
from unittest.mock import patch, MagicMock
from app.modules.rating.services import RatingService


@pytest.fixture
def rating_service():
    return RatingService()


def test_add_or_remove_rating_add(rating_service):
    with patch.object(rating_service.repository, 'add') as mock_add, \
         patch.object(rating_service.repository, 'commit') as mock_commit, \
         patch.object(rating_service, 'user_already_rated_dataset', return_value=False) as mock_user_already_rated:

        dataset_id = 1
        user_id = 1

        rating_service.add_or_remove_rating(dataset_id, user_id)

        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        mock_user_already_rated.assert_called_once_with(dataset_id, user_id)


def test_add_or_remove_rating_remove(rating_service):
    with patch.object(rating_service, 'remove_ratings') as mock_remove_ratings, \
         patch.object(rating_service, 'user_already_rated_dataset', return_value=True) as mock_user_already_rated:

        dataset_id = 1
        user_id = 1

        rating_service.add_or_remove_rating(dataset_id, user_id)

        mock_remove_ratings.assert_called_once_with(dataset_id, user_id)
        mock_user_already_rated.assert_called_once_with(dataset_id, user_id)


def test_remove_ratings(rating_service):
    with patch.object(rating_service.repository, 'get_by_dataset_id_and_user_id') as mock_get_by_datasetid_and_userid, \
         patch.object(rating_service.repository, 'delete') as mock_delete, \
         patch.object(rating_service.repository, 'commit') as mock_commit:

        mock_ratings = [MagicMock(id=1), MagicMock(id=2)]
        mock_get_by_datasetid_and_userid.return_value = mock_ratings

        dataset_id = 1
        user_id = 1

        rating_service.remove_ratings(dataset_id, user_id)

        assert mock_delete.call_count == len(mock_ratings)
        mock_commit.assert_called_once()


def test_user_already_rated_dataset(rating_service):
    with patch.object(rating_service.repository, 'get_by_dataset_id_and_user_id') as mock_get_by_datasetid_and_userid:

        dataset_id = 1
        user_id = 1

        mock_get_by_datasetid_and_userid.return_value = [MagicMock(id=1)]

        result = rating_service.user_already_rated_dataset(dataset_id, user_id)

        assert result is True
        mock_get_by_datasetid_and_userid.assert_called_once_with(dataset_id, user_id)


def test_user_already_rated_dataset_no_ratings(rating_service):
    with patch.object(rating_service.repository, 'get_by_dataset_id_and_user_id') as mock_get_by_datasetid_and_userid:

        dataset_id = 1
        user_id = 1

        mock_get_by_datasetid_and_userid.return_value = []

        result = rating_service.user_already_rated_dataset(dataset_id, user_id)

        assert result is False
        mock_get_by_datasetid_and_userid.assert_called_once_with(dataset_id, user_id)


def test_get_total_ratings_for_dataset(rating_service):
    with patch.object(rating_service.repository, 'get_query') as mock_get_query:

        dataset_id = 1
        mock_query = MagicMock()
        mock_query.filter_by.return_value.count.return_value = 5
        mock_get_query.return_value = mock_query

        result = rating_service.get_total_ratings_for_dataset(dataset_id)

        assert result == 5
        mock_query.filter_by.assert_called_once_with(dataset_id=dataset_id)


def test_get_total_ratings_for_dataset_no_ratings(rating_service):
    with patch.object(rating_service.repository, 'get_query') as mock_get_query:

        dataset_id = 1
        mock_query = MagicMock()
        mock_query.filter_by.return_value.count.return_value = 0
        mock_get_query.return_value = mock_query

        result = rating_service.get_total_ratings_for_dataset(dataset_id)

        assert result == 0
        mock_query.filter_by.assert_called_once_with(dataset_id=dataset_id)
