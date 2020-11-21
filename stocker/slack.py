import json
import logging

import requests
from retry import retry

from config import SlackConfig


class SlackHandler(logging.StreamHandler):

    def __init__(self):
        super(SlackHandler, self).__init__()

    def emit(self, record):
        msg = self.format(record)
        self.send_message(msg)

    @retry(tries=5, delay=2, backoff=2)
    def send_message(self, message: str):

        if isinstance(message, dict):
            message = json.dumps(message, indent=4, ensure_ascii=False)
        if isinstance(message, list):
            message = ','.join(str(message))

        requests.post(SlackConfig.URL,
                      data=json.dumps({'text': message}))
