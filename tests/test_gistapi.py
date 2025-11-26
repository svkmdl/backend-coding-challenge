import unittest
from unittest.mock import patch
from gistapi.gistapi import gists_for_user, gist_for_gist_id, search_pattern_in_gist_file, app

# Unit tests (used ref : https://medium.com/@moraneus/the-art-of-mocking-in-python-a-comprehensive-guide-8b619529458f)
class TestUtils(unittest.TestCase):
    @patch('gistapi.gistapi.requests.get')
    def test_gists_for_user(self, mock_get: patch) -> None :
        mock_response = mock_get.return_value
        expected_data = {"foo" : "bar"}
        mock_response.json.return_value = expected_data
        username = 'justdionysus'
        expected_url = 'https://api.github.com/users/justdionysus/gists'
        actual_data = gists_for_user(username)
        self.assertEqual(actual_data, expected_data)
        mock_get.assert_called_once_with(expected_url)

    @patch('gistapi.gistapi.requests.get')
    def test_gist_for_gist_id(self, mock_get: patch) -> None :
        mock_response = mock_get.return_value
        expected_data = {"foo" : "bar"}
        mock_response.json.return_value = expected_data
        gist_id = '7d7218b569014139f74e27a75ffc5293'
        expected_url = 'https://api.github.com/gists/7d7218b569014139f74e27a75ffc5293'
        actual_data = gist_for_gist_id(gist_id)
        self.assertEqual(actual_data, expected_data)
        mock_get.assert_called_once_with(expected_url)

    @patch('gistapi.gistapi.requests.get')
    def test_search_pattern_in_gist_file(self, mock_get: patch) -> None :
        mock_response = mock_get.return_value.__enter__.return_value  # actual object used as 'response' inside the 'with' block
        mock_response.iter_content.return_value = ['ABC KOLKATA XYZ'.encode("utf-8")]
        expected_url = 'https://gist.githubusercontent.com/maneetgoyal/38229f221e54b0864437ff00ccea39aa/raw/238926e17a78cacee6c643313bf05c71b850d431/indian-districts.json'
        actual_data = search_pattern_in_gist_file( expected_url, 'KOLKATA')
        self.assertTrue(actual_data)
        mock_get.assert_called_once_with(expected_url, stream = True)

# Integration tests (used refs : https://flask.palletsprojects.com/en/stable/testing/ and https://codethechange.stanford.edu/guides/guide_flask_unit_testing.html)
class TestSearchEndpoint(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    @patch("gistapi.gistapi.gists_for_user", return_value=[{"id": "123"}])
    @patch("gistapi.gistapi.gist_for_gist_id", return_value={"files":{"keybase.md":{"filename":"keybase.md","type":"text/markdown","language":"Markdown","raw_url":"url","size":2189,"truncated":True,"content":"qwerty","encoding":"utf-8"}}})
    @patch("gistapi.gistapi.search_pattern_in_gist_file", return_value=True)
    def test_search_calls_helpers_and_returns_200_with_matches(self, mock_search_pattern_in_gist_file, mock_gist_for_gist_id, mock_gists_for_user):
        payload = {"username" : "justdionysus", "pattern" : "import requests"}
        response = self.client.post('/api/v1/search', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("matches", data)
        mock_gists_for_user.assert_called_once()
        mock_gist_for_gist_id.assert_called_once()
        mock_search_pattern_in_gist_file.assert_called_once()
if __name__ == '__main__':
    unittest.main()