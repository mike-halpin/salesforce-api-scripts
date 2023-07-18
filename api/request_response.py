import requests


def get_status_code(response: requests.Response):
    return response.status_code


def get_error_message(response: requests.Response):
    message = ''
    if get_status_code(response) != 200:
        message = response.json()[0]['message']
    return message


def get_error_code(response: requests.Response):
    code = ''
    if get_status_code(response) != 200:
        code = response.json()[0]['errorCode']
    return code


def get_response_text(response: requests.Response):
    return response.text
