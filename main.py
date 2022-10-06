import os
import hashlib
import base64
import requests
import json

BASE_URL = 'https://sid.demo.sk.ee/smart-id-rp/v2'
PERSON_ID = 39803273710
COUNTRY_CODE = 'EE'
IDENTITY_TYPE = 'PNO'
DEMO_UUID = '00000000-0000-0000-0000-000000000000'
DEMO_PARTY_NAME = 'DEMO'


def generate_hash_sha512():
    hash_function = hashlib.sha512()
    hash_function.update(bytearray(os.urandom(64)))
    return base64.b64encode(hash_function.digest())


def init_session():
    url = f'{BASE_URL}/authentication/etsi/{IDENTITY_TYPE + COUNTRY_CODE}-{PERSON_ID}'
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'relyingPartyUUID': DEMO_UUID,
        'relyingPartyName': DEMO_PARTY_NAME,
        'hash': generate_hash_sha512().decode('utf-8'),
        'hashType': 'SHA512',
        'allowedInteractionsOrder': [
            {
                'type': 'displayTextAndPIN',
                'displayText60': 'Up to 60 characters of text here..'
            }
        ]
    }
    req = requests.request("POST", url, headers=headers, data=convert_to_json(payload))
    return req.json()


def convert_to_json(payload):
    return json.dumps(payload).replace('"', '\"')


def session_status(session_id):
    timeout_ms = 2000
    url = f'{BASE_URL}/session/{session_id}?timeoutMs={timeout_ms}'
    req = requests.get(url)
    return req.json()


if __name__ == '__main__':
    session_id = init_session()['sessionID']
    status = session_status(session_id)['state']
    num_retries = 10

    while status != 'COMPLETE' and num_retries != 0:
        status = session_status(session_id)['state']
        print(status)
        num_retries -= 1

    print('FINAL STATUS: ' + status)
