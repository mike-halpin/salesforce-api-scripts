import re
import requests

import salesforce.log_config as log_config

logger = log_config.get_logger(__name__)

class ParsedResponse:
    def __init__(self, response: requests.Response, query_string: str):
        self._response = response
        self._query_string = query_string
        self._fields = []
    def __str__(self):
        return f"status_code: {self.get_status_code()}\nerror_message: {self.get_error_message()}\nerror_code: {self.get_error_code()}\nresponse_text: {self.get_response_text()}"

    def export_dto(self):
        logger.debug("Exporting DTO")
        logger.debug('statusCode: ' + str(self.get_status_code()))
        logger.debug('errorMessage: ' + str(self.get_error_message()))
        logger.debug('errorCode: ' + str(self.get_error_code()))
        logger.debug('responseText: ' + str(self.get_response_text()))
        logger.debug('queryString: ' + str(self._query_string))
        logger.debug('hasError: ' + str(self.is_error()))
        logger.debug('recordCount: ' + str(self.get_record_count()))
        records = self.get_records()
        return {
            'records': records,
            'statusCode': self.get_status_code(),
            'errorMessage': self.get_error_message(),
            'errorCode': self.get_error_code(),
            'responseText': self.get_response_text(),
            'queryString': self._query_string,
            'hasError': self.is_error(),
            'recordCount': self.get_record_count()
        }

    def get_status_code(self):
        try:
            return int(self._response.status_code)
        except AttributeError as e:
            logger.error("AttributeError occurred: %s", e)
        except TypeError as e:
            logger.error("TypeError occurred: %s", e)
        return 0 

    def get_error_message(self):
        message = ''
        if not self.get_status_code() - 200 < 100: # 200-299 is success
            try:
                message = self._response.json()['records'][0]['attributes']['type']
            except TypeError as e:
                message = self._response.json()[0]['message']
            except (AttributeError, KeyError, IndexError) as e:
                logger.error("Error parsing message from self, response: %s", e)
        return message


    def get_error_code(self):
        code = ''
        if self.get_status_code():
            if not self.get_status_code() - 200 < 100: # 200-299 is success
                try:
                    code = self._response.json()[0]['errorCode']
                except (AttributeError, KeyError, IndexError, TypeError) as e:
                    logger.error("Error parsing errorCode from self, response: %s", e)
        return code


    def get_response_text(self):
        try:
            return self._response.text
        except Exception as e:
            logger.error("Error getting response text: %s", e)
            return '' 

    @property
    def fields(self):
        return self._fields
    
    @fields.setter
    def fields(self, fields):
        self._fields = fields


    def is_error(self):
        is_error = True
        if self.get_status_code():
            logger.debug("Status code: %s", self.get_status_code())
            if int(self.get_status_code()) - 200 < 100: # 200-299 is success
                if self.get_error_code() == '' and self.get_error_message() == '':
                    is_error = False
        return is_error

    def is_object_error(self):
        """Returns True if the error matches a known error string, False otherwise."""
        object_error_patters = {
            'is_invalid': 'sObject type (.*?) is not supported.'  # INVALID_TYPE
        }
        error_code = self.get_error_code()
        error_message = self.get_error_message()
        if error_code == 'INVALID_TYPE':
            error_match = next((re.search(pattern, error_message).group(1) for pattern in object_error_patters.values() if re.search(pattern, error_message)), '')
            if error_match:
                return True
        return False

    def is_field_error(self):
        """Returns True if the error matches a known error string, False otherwise."""
        field_error_patterns = {
            'is_invalid': 'Invalid field: \'(.*?)\'',
            'is_aggregate': 'field (.*?) does not support aggregate operator',
        }
        error_code = self.get_error_code()
        error_message = self.get_error_message()
        if error_code == 'INVALID_FIELD' or error_code == 'MALFORMED_QUERY':
            field_match = next((re.search(pattern, error_message).group(1) for pattern in field_error_patterns.values() if re.search(pattern, error_message)), '')
            if field_match:
                return True

        return False

    def is_query_error(self):
        """Returns True if the error matches a known error string, False otherwise."""
        if self.is_field_error():  # We don't consider field errors to be query errors.
            return False
        else:
            query_error_patterns = {
                'is_missing_fields': 'unexpected token: \'(.*?)\'',
                'alias_bug': 'maximum number of aliased fields exceeded: (.*?)',
            }
            error_code = self.get_error_code()
            error_message = self.get_error_message()
            if error_code == 'MALFORMED_QUERY':
                query_match = next((re.search(pattern, error_message).group(1) for pattern in query_error_patterns.values() if re.search(pattern, error_message)), '')
                if query_match in ['FROM']:  # Is missing fields
                    return True
                elif query_match in [100]:  # Alias bug
                    logger.debug("Query error: %s", error_message)
                    return True

        return False

    def is_aggregate(self):
        """Returns True if the error matches a known error string, False otherwise."""
        is_aggregate = False
        try:
            self._response.json()['records'][0]['attributes']['type'] == 'AggregateResult'
            is_aggregate = True
        except (AttributeError, KeyError, IndexError, TypeError) as e:
            logger.error("Error {#eisag1} checking ParsedResponse()._response.json()['records'][0]['attributes']['type'] == 'AggregateResult', response: %s", e)
            raise e
        return is_aggregate

    def get_records(self):
        try:
            records = self._response.json()['records']
        except (AttributeError, KeyError, TypeError) as e:
            logger.error("Error parsing records: %s", e)
            records = {}
        return records

    def get_record_count(self):
        """Returns the record count from a query result."""
        record_count = 0
        try:
            record_count = self._response.json()['totalSize']
        except TypeError as e:
            logger.info("No records found: %s", e)
        return record_count

def extract_fields_from_query(query):
    """Extracts fields from a query string.
    Returns a list of fields.
    """
    fields = []
    try:
        fields = re.findall(r'(?<=SELECT )(.*?)(?= FROM)', query)[0].split(', ')
    except IndexError as e:
        logger.error("Error extracting fields from query: %s", e)
    return fields

def extract_fields_from_request_response(query_result):
    """Extracts fields from a query result.
    Returns a list of fields.
    """
    fields = []
    try:
        fields = query_result['records'][0].keys()
    except IndexError as e:
        logger.error("Error extracting fields from query result: %s", e)
    return fields
