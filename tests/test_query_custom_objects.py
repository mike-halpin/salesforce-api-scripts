import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import re
import requests
import pytest
from unittest.mock import patch, Mock
import salesforce.api.query as query

AUTHENTICATE_API_FUNCTION = 'query.authenticate.authenticate_api'
EXTRACT_FIELDS_FUNCTION = 'query.format.extract_fields_from_query_string' 
REQUESTS_GET_FUNCTION = 'salesforce.api.query.requests.get'
PARSEDRESPONSE_EXPORT_DTO = 'query.ParsedResponse.export_dto'

def mock_setup(mock_authenticate_api, mock_extract_fields, mock_get, mock_parsedresponse, return_value, hasErrors=True):
    mock_authenticate_api.return_value = ('session_id', 'https://server_url/services/data')
    mock_extract_fields.return_value = ['field1', 'field2']
    mock_parsedresponse.return_value = {
            'records': return_value['records'],
            'statusCode': return_value['statusCode'],
            'errorType': return_value['errorType'],
            'errorMessage': return_value['errorMessage'],
            'responseText': return_value['responseText'],
            'queryString': return_value['queryString'],
            'errors': [{'errorCode': return_value['errorType'], 'message': return_value['errorMessage']}],
            'hasError': True if return_value['errorType'] or return_value['errorMessage'] else False
            }

def test_match_custom_object_ids_to_field_names():
    pass
def test_match_custom_object_ids_to_object_names():
    pass
"""
def test_invalid_type_response():
    with  patch(AUTHENTICATE_API_FUNCTION) as mock_authenticate_api, patch(EXTRACT_FIELDS_FUNCTION) as mock_extract_fields, patch(REQUESTS_GET_FUNCTION) as mock_get, patch(PARSEDRESPONSE_EXPORT_DTO) as mock_parsedresponse:
        records = {}
        status_code = 400
        error_type = 'INVALID_TYPE'
        error_message = ''
        response_text = ''
        query_string = 'SELECT hed__Course_Offering__c), hed__Facility__c), hed__Time_Block__c), FROM hed__Course_Offering_Schedule__c'
        mock_setup(mock_authenticate_api, mock_extract_fields, mock_get, mock_parsedresponse, {'records': records, 'statusCode': status_code, 'errorType': error_type, 'errorMessage': error_message, 'responseText': response_text, 'queryString': query_string})
        result = query.run_query_using_requests('')
        assert result['hasError'] == True

# Test for Invalid field
def test_invalid_field_response():
    with  patch(AUTHENTICATE_API_FUNCTION) as mock_authenticate_api, patch(EXTRACT_FIELDS_FUNCTION) as mock_extract_fields, patch(REQUESTS_GET_FUNCTION) as mock_get, patch(PARSEDRESPONSE_EXPORT_DTO) as mock_parsedresponse:
        records = {}
        status_code = 400
        error_type = 'INVALID_FIELD'
        error_message = 'INVALID_FIELD: SELECT COUNT(Answer__c), COUNT(Question__c), COUNT(Article_Body__c) FROM Knowledge__c'
        response_text = ''
        query_string = 'SELECT hed__Course_Offering__c), hed__Facility__c), hed__Time_Block__c), FROM hed__Course_Offering_Schedule__c'
        mock_setup(mock_authenticate_api, mock_extract_fields, mock_get, mock_parsedresponse, {'records': records, 'statusCode': status_code, 'errorType': error_type, 'errorMessage': error_message, 'responseText': response_text, 'queryString': query_string})
        result = query.run_query_using_requests('')
        assert result['hasError'] == True

# Test for Malformed query
def test_malformed_query_response():
    with  patch(AUTHENTICATE_API_FUNCTION) as mock_authenticate_api, patch(EXTRACT_FIELDS_FUNCTION) as mock_extract_fields, patch(REQUESTS_GET_FUNCTION) as mock_get, patch(PARSEDRESPONSE_EXPORT_DTO) as mock_parsedresponse:
        records = {}
        status_code = 400
        error_type = 'MALFORMED_QUERY'
        error_message = ''
        response_text = ''
        query_string = 'SELECT hed__Course_Offering__c), hed__Facility__c), hed__Time_Block__c), FROM hed__Course_Offering_Schedule__c'
        mock_setup(mock_authenticate_api, mock_extract_fields, mock_get, mock_parsedresponse, {'records': records, 'statusCode': status_code, 'errorType': error_type, 'errorMessage': error_message, 'responseText': response_text, 'queryString': query_string})
        result = query.run_query_using_requests('')
        assert result['hasError'] == True

# Test for none of the above
def test_unhandled_response_error():
    with  patch(AUTHENTICATE_API_FUNCTION) as mock_authenticate_api, patch(EXTRACT_FIELDS_FUNCTION) as mock_extract_fields, patch(REQUESTS_GET_FUNCTION) as mock_get, patch(PARSEDRESPONSE_EXPORT_DTO) as mock_parsedresponse:
        records = {}
        status_code = 400
        error_type = ''
        error_message = ''
        response_text = ''
        query_string = 'SELECT field1, field2 FROM Table'
        mock_setup(mock_authenticate_api, mock_extract_fields, mock_get, mock_parsedresponse, {'records': records, 'statusCode': status_code, 'errorType': error_type, 'errorMessage': error_message, 'responseText': response_text, 'queryString': query_string})
        result = query.run_query_using_requests('')



"""
# Run the tests
if __name__ == '__main__':
    pytest.main(['-v', __file__])


