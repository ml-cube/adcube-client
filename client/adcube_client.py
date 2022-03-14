import asyncio
import datetime
import json
import uuid
from copy import deepcopy
from time import sleep

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


class SocketManager:

    def __init__(self):
        self._websocket = None
        self.received_messages = None

    @property
    def _socket(self):
        if self._websocket is None or self._websocket.closed:
            try:
                self._websocket = websockets.connect(WEBSOCKET_ENDPOINT)
            except Exception as ex:
                raise ConnectionException(ex)
        return self._websocket

    def _generate_request_id(self):
        return uuid.uuid4()

    async def send_request_message(self, message, action, authorization):
        request_id = self._generate_request_id()
        payload = {
            'authorization': authorization,
            'action': action,
            'message': message,
            'requestId': request_id
        }
        self._socket.send(json.dumps(payload))
        # Consume and save messages until the desired message is received
        while request_id not in self.received_messages:
            message = self._socket.recv()
            message = json.loads(message)
            request_id = message['requestId']
            self.received_messages[request_id] = deepcopy(message)

        # Remove the message, to avoid memory consumption
        message = self.received_messages[request_id]
        del self.received_messages[request_id]
        return message

    def close_socket(self):
        if self._websocket is not None and not self._websocket.closed():
            self._websocket.close()


class AsyncResult:
    def __init__(self, result_future):
        self._result = None
        self._result_future = result_future

    def _receive_result(self):
        if self._result is None:
            loop = asyncio.new_event_loop()
            self._result = loop.run_until_complete(self._result_future)
            self._result_future = None
        return self._result


class BudoptResult(AsyncResult):

    @property
    def allocations(self):
        return self._receive_result()

    @allocations.setter
    def allocations(self, value):
        self._result = value


class SpendoptResult(AsyncResult):

    @property
    def predictions(self):
        return self._receive_result()

    @predictions.setter
    def predictions(self, value):
        self._result = value


class ADCubeClient:

    def __init__(self, api_key, proxy=None):
        if proxy is not None:
            raise NotImplementedError

        self._api_key = api_key

        self._socket_manager = SocketManager()

    async def compute_budopt(self):

        payload = {}

        try:
            future = self._socket_manager.send_request_message(
                message=payload,
                action='budopt',
                authorization=self._api_key
            )

        except Exception as e:
            raise ConnectionException(e)

        return BudoptResult(future)

    def compute_spendopt(self):
        payload = {}

        try:
            future = self._socket_manager.send_request_message(
                message=payload,
                action='spendopt',
                authorization=self._api_key
            )

        except Exception as e:
            raise ConnectionException(e)

        return BudoptResult(future)

    def close(self):
        pass
