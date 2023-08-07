from xml.etree import ElementTree as ET
from unittest.mock import patch, Mock, MagicMock 
import pytest 
import requests
from authenticate import authenticate_tooling_api 
from environment import get_salesforce_password, get_salesforce_username, get_salesforce_access_token

class TestAuthenticate(unittest.TestCase):

    @patch('requests.post')
    @patch('requests.raise_for_status')
    def test_authenticate_tooling_api(self, mock_post, mock_raise_for_status):
        mock_raise_for_status.return_value = None
        username = 'username'
        password = 'password'
        token = 'token'
        mock_response = MagicMock()
        mock_response.return_value = 'test'
        mock_post.return_value = MockResponse('test')
        response = authenticate_tooling_api(username, password, token)

        self.assertEqual(response, 'test')
   

hardlink