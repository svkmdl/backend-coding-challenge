import unittest
from unittest.mock import patch
from gistapi.gistapi import gists_for_user

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
if __name__ == '__main__':
    unittest.main()