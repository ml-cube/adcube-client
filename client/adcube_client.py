import datetime
import json
import uuid

import requests
import websockets

AUTH_ENDPOINT = ''
WEBSOCKET_ENDPOINT = ''


class ConnectionException(Exception):
    pass


class RequestException(Exception):
    pass


class AuthenticationException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


class ADCubeClient:

    def _generate_request_id(self):
        return uuid.uuid4()

    def __init__(self, api_key, proxy=None):
        if proxy is not None:
            raise NotImplementedError

        payload = {
            'api_key': api_key
        }
        try:
            response = requests.post(AUTH_ENDPOINT, data=json.dumps(payload))

            # TODO expand handling of different status codes
            if response.status_code != 200:
                raise RequestException

            json_response = response.json()

            if 'jwt' not in json_response['authentication']:
                raise AuthenticationException

            self._jwt = json_response['authentication']['jwt']

        except Exception as e:
            raise ConnectionException(e)

        self._socket = None

    def _open_socket(self):
        if not self._socket or self._socket.closed:
            try:
                self._socket = websockets.connect(WEBSOCKET_ENDPOINT)
            except Exception as ex:
                raise ConnectionException(ex)

    def _send_request_message(self, payload):
        try:
            self._socket.send(payload)
        except Exception as ex:
            raise ConnectionException(ex)

    def compute_budopt(self):
        request_id = self._generate_request_id()
        self._open_socket()

        payload = {}

        self._send_request_message(payload)

    def compute_spendopt(self):
        request_id = self._generate_request_id()
        self._open_socket()

        payload = {}

        self._send_request_message(payload)

    def close(self):
        pass
