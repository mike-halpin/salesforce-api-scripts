import requests
from xml.etree import ElementTree as ET
import environment as environment

def authenticate_api(username, password, security_token, sandbox=False):
    endpoint = 'https://test.salesforce.com/services/Soap/u/58.0' if sandbox else 'https://login.salesforce.com/services/Soap/u/58.0'

    response = requests.post(endpoint, headers=get_header(), data=get_body(username, password, security_token))
    response.raise_for_status()

    tree = get_tree(response.content)

    return get_session_id(tree, get_namespaces()), get_server_url(tree, get_namespaces()) 

def get_header():
    return { 'content-type': 'text/xml',
            'charset': 'UTF-8',
            'SOAPAction': 'login'}

def get_body(username, password, security_token):
    body = f"""<?xml version="1.0" encoding="utf-8" ?>
        <env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
          <env:Body>
            <n1:login xmlns:n1="urn:partner.soap.sforce.com">
              <n1:username>{username}</n1:username>
              <n1:password>{password}{security_token}</n1:password>
            </n1:login>
          </env:Body>
        </env:Envelope>"""
    return body

def get_tree(response):
    return ET.fromstring(response)

def get_namespaces():
    return {'urn': 'urn:partner.soap.sforce.com'}

def get_session_id(tree, namespaces):
    return tree.find('.//urn:sessionId', namespaces).text

def get_server_url(tree, namespaces):
    return tree.find('.//urn:serverUrl', namespaces).text


def main():
    session_id, server_url = authenticate_api(environment.get_salesforce_username(), environment.get_salesforce_password(), environment.get_salesforce_access_token(), sandbox=True)
    print(session_id)
    print(server_url)

if __name__ == "__main__":
    main()
