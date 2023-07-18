import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import re
import requests
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest
import pandas as pd
import environment 
import dataframe 
import authenticate 
import format
import request_response

environment.load_environment_variables()

def query_custom_objects_names():
    query_string = "SELECT Id, DeveloperName, NamespacePrefix FROM CustomObject"

    # Query Tooling API
    records = query_tooling_api(query_string)

    if records is not None:
        # Convert records to a DataFrame
        df = dataframe.convert_records_to_dataframe(records)
        return df
    else:
        return None


def query_custom_field_names():
    query_string = "SELECT TableEnumOrId, DeveloperName, NamespacePrefix FROM CustomField"

    # Query Tooling API
    records = query_tooling_api(query_string)

    if records is not None:
        # Convert records to a DataFrame
        df = dataframe.convert_records_to_dataframe(records)
        return df
    else:
        return None


def query_tooling_api(query, sandbox=False, is_tooling=True):
    # Login to Salesforce
    session_id, server_url = authenticate.authenticate_api(environment.get_salesforce_username(), environment.get_salesforce_password(), environment.get_salesforce_access_token(), sandbox=True)

    # Construct API endpoint
    if is_tooling:
        api_endpoint = server_url.split('/services')[0] + '/services/data/v58.0/tooling/query'
    else:
        api_endpoint = server_url.split('/services')[0] + '/services/data/v58.0/query'

    # Request headers
    headers = {
        'Authorization': 'Bearer ' + session_id,
        'Content-Type': 'application/json'
    }

    # Request payload
    payload = {
        'q': query
    }

    # Send request to the Tooling API
    response = requests.get(api_endpoint, headers=headers, params=payload)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        return data['records']
    else:
        print("Error occurred: " + response.text)
        return None

def get_salesforce_interface():
    sf = Salesforce(username=environment.get_salesforce_username(), password=environment.get_salesforce_password(), security_token=environment.get_salesforce_access_token(), domain='test')
    return sf

def query_field_descriptions_by_object(object_name, sf=None):
    if not sf:
        sf = get_salesforce_interface()
    fields = getattr(sf, object_name).describe()['fields']
    return fields

def run_query_using_requests(query_string):
    # Login to Salesforce
    session_id, server_url = authenticate.authenticate_api(environment.get_salesforce_username(), environment.get_salesforce_password(), environment.get_salesforce_access_token(), sandbox=True)
    # Request headers
    headers = {
        'Authorization': 'Bearer ' + session_id,
        'Content-Type': 'application/json'
    }
    # Send request to the API
    to_return = {
        'status_code': 0,
        'error_code': '',
        'error_message': '',
        'records': {},
        'query_string': query_string
    }
    retry_limit = len(format.extract_fields_from_query_string(query_string))
    while retry_limit > 0:  # Retry until all fields are queried successfully, after that, we need to break the loop
        retry_limit -= 1
        payload = {
            'q': query_string
        }
        to_return['raw_response'] = requests.get(server_url.split('/services')[0] + '/services/data/v57.0/query', headers=headers, params=payload)
        to_return['status_code'] = request_response.get_status_code(to_return['raw_response'])
        to_return['error_code'] = request_response.get_error_code(to_return['raw_response'])
        to_return['error_message'] = request_response.get_error_message(to_return['raw_response'])
        to_return['response_text'] = request_response.get_response_text(to_return['raw_response'])
        to_return['query_string'] = query_string
        print("Response.text = " + to_return['response_text'])
        is_invalid_sobject = to_return['error_code'] == 'INVALID_TYPE'
        is_invalid_field = to_return['error_code'] == 'INVALID_FIELD'
        is_malformed_query = to_return['error_code'] == 'MALFORMED_QUERY'
        if to_return['status_code'] == 200:
            data = to_return['raw_response'].json()
            to_return['records'] = data['records']

        elif is_invalid_sobject:
            break

        elif is_invalid_field or is_malformed_query:  # The field can't be queried via API, remove it from the query
            error_patterns = {
                'is_invalid': 'Invalid field: \'(.*?)\'',
                'is_aggregate': 'field (.*?) does not support aggregate operator',
                # Add more patterns here as needed.
            }
            field = next((re.search(pattern, to_return['error_message']).group(1) for pattern in error_patterns.values() if re.search(pattern, to_return['error_message'])), '')
            try:
                print(query_string)
                print(field)
                query_string = re.sub('\s*COUNT\(' + re.escape(field) + '\)?\,?\s*', ' ', query_string)
            except TypeError as e:
                print(e)
            except AttributeError as e:
                print(e)
            continue

        else:
            raise ValueError("Error occurred: " + to_return['response_text'])

    return to_return

def run_query_using_simple_salesforce(query):
    sf = get_salesforce_interface()
    try:
        records = sf.query(query)
        df = dataframe.convert_records_to_dataframe(records['records'])
        if sum(df.values[0][1:]) == 0:
            return pd.DataFrame()
        for record in records['records']:
            for field in record:
                print(field)

    except SalesforceMalformedRequest as e:
        print(e)
        df = pd.pandas.DataFrame()
    if not df.empty:
        print('breakpoint')

    return df

def get_custom_object_names():
    df = query_custom_objects_names()
    df = format.format_api_names_from_tooling_api(df)
    return df['DeveloperName'].tolist()

def get_custom_object_ids():
    df = query_custom_objects_names()
    return df['Id'].tolist()

def get_custom_field_names():
    df = query_custom_field_names()
    df = format.format_api_names_from_tooling_api(df)
    return df['DeveloperName'].tolist()

def match_custom_object_ids_to_field_names():
    fields = query_custom_field_names()
    fields = dataframe.format_api_names_from_tooling_api(fields)
    object_ids_to_field_names = fields.groupby('TableEnumOrId')['DeveloperName'].apply(list).to_dict()

    return object_ids_to_field_names

def match_custom_object_ids_to_object_names():
    objects = query_custom_objects_names()
    objects = format.format_api_names_from_tooling_api(objects)
    object_ids_to_object_names = objects.set_index('Id')['DeveloperName'].to_dict()
    return object_ids_to_object_names

def main():
    pass

if __name__ == "__main__":
    main()
