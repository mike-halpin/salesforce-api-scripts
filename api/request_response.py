import requests

import salesforce.log_config as log_config

logger = log_config.get_logger(__name__)



class ParsedResponse:
    def __init__(self, response: requests.Response, query_string: str):
        self._response = response
        self._query_string = query_string
        self._errors = [{'error_message': '', 'error_code': ''}]

    def __str__(self):
        return f"status_code: {self.status_code}\nerror_message: {self.error_message}\nerror_code: {self.error_code}\nresponse_text: {self.response_text}"

    def export_dto(self):
        return {
            'records': self._response.json(),
            'statusCode': self.get_status_code(self._response),
            'errorMessage': self.get_error_message(self._response),
            'errorCode': self.get_error_code(self._response),
            'responseText': self.get_response_text(self._response),
            'queryString': self._query_string,
            'errors': self._errors,
            'hasError': self.has_errors()
        }

    def get_status_code(self):
        try:
            return self._response.statusCode
        except AttributeError as e:
            logger.error("AttributeError occurred: %s", e)
            return '' 


    def get_error_message(self):
        message = ''
        try:
            message = self._response.json()[0]['message']
        except (AttributeError, KeyError, IndexError, TypeError) as e:
            logger.error("Error parsing message from self, response: %s", e)
        return message


    def get_error_code(self):
        code = ''
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

    def has_errors(self):
        is_error = False
        if len(self.errors) > 1:
            is_error = True
        elif self.errors[0]['error_message'] != '' or self.errors[0]['error_code'] != '':
            is_error = True
        else:
            pass
        return is_error
