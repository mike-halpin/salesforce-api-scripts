import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

import query  

def test_query_custom_objects_names():
    with patch('query.query_tooling_api', return_value=[{'Id': '1', 'DeveloperName': 'Test', 'NamespacePrefix': None}]):
        with patch('query.dataframe.convert_records_to_dataframe', return_value=pd.DataFrame([{'Id': '1', 'DeveloperName': 'Test', 'NamespacePrefix': None}])):
            result = query.query_custom_objects_names()
            assert result.equals(pd.DataFrame([{'Id': '1', 'DeveloperName': 'Test', 'NamespacePrefix': None}]))

def test_query_custom_field_names():
    with patch('query.query_tooling_api', return_value=[{'TableEnumOrId': '1', 'DeveloperName': 'Test', 'NamespacePrefix': None}]):
        with patch('query.dataframe.convert_records_to_dataframe', return_value=pd.DataFrame([{'TableEnumOrId': '1', 'DeveloperName': 'Test', 'NamespacePrefix': None}])):
            result = query.query_custom_field_names()
            assert result.equals(pd.DataFrame([{'TableEnumOrId': '1', 'DeveloperName': 'Test', 'NamespacePrefix': None}]))

def test_query_tooling_api():
    with patch('query.authenticate.authenticate_tooling_api', return_value=('session_id', 'http://server_url/services/data')):
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'records': []}
            mock_get.return_value = mock_response
            result = query.query_tooling_api('SELECT Id FROM Account')
            assert result == []

def test_get_salesforce_interface():
    with patch('query.environment.get_salesforce_username', return_value='test_user'):
        with patch('query.environment.get_salesforce_password', return_value='test_password'):
            with patch('query.environment.get_salesforce_access_token', return_value='test_token'):
                with patch('query.Salesforce') as mock_sf:
                    query.get_salesforce_interface()
                    mock_sf.assert_called_with(username='test_user', password='test_password', security_token='test_token', domain='test')

# Add similar test cases for the remaining functions

