import os
import re
import sys

import pandas as pd
import requests
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest

import analysis.dataframe as dataframe
import salesforce.api.authenticate as authenticate
from salesforce.api.request_response import ParsedResponse
import salesforce.log_config as log_config
import utilities.environment as environment
import utilities.format as format

# Configure logging
logger = log_config.get_logger(__name__)

# Add the project root directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

environment.load_environment_variables()

def run_query_using_requests(query_string):
    session_id, server_url = authenticate_and_get_session()
    headers = create_headers(session_id)
    payload = prepare_payload(query_string)
    try:
        raw_response = requests.get(server_url.split('/services')[0] + '/services/data/v57.0/query', headers=headers, params=payload)
        parsed_response_dto = handle_response(raw_response, query_string)
        logger.info("Response.text = %s", parsed_response_dto['responseText'])
    except requests.exceptions.RequestException as e:
        logger.error("Error occurred while querying Salesforce API: %s", e)
        parsed_response_dto = {}

    return parsed_response_dto

def authenticate_and_get_session():
    session_id, server_url = authenticate.authenticate_api(environment.get_salesforce_username(),
                                                           environment.get_salesforce_password(),
                                                           environment.get_salesforce_access_token(),
                                                           sandbox=True)
    return session_id, server_url

def create_headers(session_id):
    headers = {
            'Authorization': 'Bearer ' + session_id,
            'Content-Type': 'application/json'
            }
    return headers


def prepare_payload(query_string):
    payload = {
            'q': query_string
            }
    return payload

def handle_response(response, query_string):
    responseDto = ParsedResponse(response, query_string)
    return responseDto.export_dto()

def modify_query_string(query_string, error_message, error_type):
    error_patterns = {
            'is_invalid': 'Invalid field: \'(.*?)\'',
            'is_aggregate': 'field (.*?) does not support aggregate operator',
            }
    field = next((re.search(pattern, error_message).group(1) for pattern in error_patterns.values() if re.search(pattern, error_message)), '')
    try:
        logger.info("Query string before modification: %s", query_string)
        logger.info("Field causing the issue: %s", field)
        query_string = re.sub('\s*COUNT\(' + re.escape(field) + '\)?\,?\s*', ' ', query_string)
    except TypeError as e:
        logger.error("Error occurred while modifying query string: %s", e)
    except AttributeError as e:
        logger.error("Error occurred while modifying query string: %s", e)
    return query_string

def query_custom_objects_names():
    query_string = "SELECT Id, DeveloperName, NamespacePrefix FROM CustomObject"
    records = query_tooling_api(query_string)

    if records is not None:
        df = dataframe.convert_records_to_dataframe(records)
        return df
    else:
        return None

def query_custom_field_names():
    query_string = "SELECT TableEnumOrId, DeveloperName, NamespacePrefix FROM CustomField"
    records = query_tooling_api(query_string)

    if records is not None:
        df = dataframe.convert_records_to_dataframe(records)
        return df
    else:
        return None

def query_tooling_api(query, sandbox=False, is_tooling=True):
    session_id, server_url = authenticate.authenticate_api(environment.get_salesforce_username(),
                                                           environment.get_salesforce_password(),
                                                           environment.get_salesforce_access_token(),
                                                           sandbox=True)

    if is_tooling:
        api_endpoint = server_url.split('/services')[0] + '/services/data/v58.0/tooling/query'
    else:
        api_endpoint = server_url.split('/services')[0] + '/services/data/v58.0/query'

    headers = {
            'Authorization': 'Bearer ' + session_id,
            'Content-Type': 'application/json'
            }

    payload = {
            'q': query
            }

    try:
        response = requests.get(api_endpoint, headers=headers, params=payload)
        response.raise_for_status()  # Raise an exception if the response status code is an error code
        data = response.json()
        return data['records']
    except requests.exceptions.RequestException as e:
        logger.error("Error occurred while querying Salesforce API: %s", e)
        return None


def get_salesforce_interface():
    sf = Salesforce(username=environment.get_salesforce_username(),
                    password=environment.get_salesforce_password(),
                    security_token=environment.get_salesforce_access_token(),
                    domain='test')
    return sf


def query_field_descriptions_by_object(object_name, sf=None):
    if not sf:
        sf = get_salesforce_interface()

    fields = getattr(sf, object_name).describe()['fields']
    return fields

def run_query_using_simple_salesforce(query):
    sf = get_salesforce_interface()

    try:
        records = sf.query(query)
        df = dataframe.convert_records_to_dataframe(records['records'])
        if sum(df.values[0][1:]) == 0:
            return pd.DataFrame()

        for record in records['records']:
            for field in record:
                logger.info(field)

    except SalesforceMalformedRequest as e:
        logger.error("Error occurred while querying Salesforce: %s", e)
        df = pd.DataFrame()

    if not df.empty:
        logger.info('breakpoint')

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
    # Add your main logic here if needed.
    pass

if __name__ == "__main__":
    main()
